package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/tools/clientcmd"
	"k8s.io/client-go/util/homedir"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"
)

func prepareKubernetesClient() *kubernetes.Clientset {
	var kubeconfig *string
	if home := homedir.HomeDir(); home != "" {
		kubeconfig = flag.String("kubeconfig", filepath.Join(home, ".kube", "config"), "(optional) absolute path to the kubeconfig file")
	} else {
		kubeconfig = flag.String("kubeconfig", "", "absolute path to the kubeconfig file")
	}
	flag.Parse()

	// use the current context in kubeconfig
	config, err := clientcmd.BuildConfigFromFlags("", *kubeconfig)
	if err != nil {
		panic(err.Error())
	}

	// create the clientset
	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		panic(err.Error())
	}

	return clientset
}

type FPGANodeState struct {
	// exported (and kube-accessible fields)
	RecentUsage                float64             `json:"recentUsage"`
	RecentReconfigurationTime  float64             `json:"recentReconfigurationTime"`
	RecentBitstreamIdentifiers map[string]struct{} `json:"recentBitstreamIdentifiers"`

	Version int `json:"version"`

	// exported state only used by metrics-collector
	UsageState           []byte
	ReconfigurationState []byte
	BitstreamState       []byte

	// internal models
	usageBasedFPGAUtilizationTracker *UsageBasedFPGAUtilizationTracker
	reconfigurationTracker           *ReconfigurationBasedFPGAUtilizationTracker
	bitstreamIdentifierTracker       *BitstreamIdentifierTracker

	manualBitstreamIdentifiers map[string]struct{}
}

const AnnotationName = "fpga-scheduling.io/fpga-state"
const StateVersion = 1

func main() {
	var port int
	flag.IntVar(&port, "port", 8080, "The port to listen on for HTTP requests")
	nodeName := flag.String("node", "", "The name of the node to be drained")
	disableKubernetes := flag.Bool("no-k8s", false, "Disable Kubernetes integration")
	flag.Parse()

	ctx, cancel := context.WithCancel(context.Background())

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigs
		cancel()
	}()

	if *nodeName == "" {
		panic("Node name is required")
	}

	fpgaNodeState := FPGANodeState{
		Version: StateVersion,

		usageBasedFPGAUtilizationTracker: NewFPGAUtilizationTracker(),
		reconfigurationTracker:           NewReconfigurationBasedFPGAUtilizationTracker(),
		bitstreamIdentifierTracker:       NewBitstreamIdentifierTracker(),
	}

	var client *kubernetes.Clientset
	if !*disableKubernetes {
		client = prepareKubernetesClient()

		node, err := client.CoreV1().Nodes().Get(ctx, *nodeName, v1.GetOptions{})
		if err != nil {
			panic(err.Error())
		}

		stateStr := node.Annotations[AnnotationName]

		if stateStr != "" {
			var tempState FPGANodeState
			err = json.Unmarshal([]byte(stateStr), &tempState)
			if err != nil {
				panic(err.Error())
			}

			if tempState.Version == StateVersion {
				err = fpgaNodeState.usageBasedFPGAUtilizationTracker.Deserialize(tempState.UsageState)
				if err != nil {
					log.Println("Error deserializing usage state: " + err.Error())
				}

				err = fpgaNodeState.reconfigurationTracker.Deserialize(tempState.ReconfigurationState)
				if err != nil {
					log.Println("Error deserializing reconfiguration state: " + err.Error())
				}

				err = fpgaNodeState.bitstreamIdentifierTracker.Deserialize(tempState.BitstreamState)
				if err != nil {
					log.Println("Error deserializing bitstream state: " + err.Error())
				}
			} else {
				log.Println("State version mismatch, starting with empty state")
			}
		}
	}

	go func() {
		for {
			select {
			case <-ctx.Done():
				log.Println("Context done, stopping sync loop")
				return
			case <-time.After(10 * time.Second):
				fpgaNodeState.usageBasedFPGAUtilizationTracker.Decay()
				fpgaNodeState.reconfigurationTracker.Decay()
				fpgaNodeState.bitstreamIdentifierTracker.Decay()

				fpgaNodeState.RecentUsage = fpgaNodeState.usageBasedFPGAUtilizationTracker.GetUtilizationMillis()
				fpgaNodeState.RecentReconfigurationTime = fpgaNodeState.reconfigurationTracker.GetRecentReconfigurationTimeMillis()
				fpgaNodeState.RecentBitstreamIdentifiers = fpgaNodeState.bitstreamIdentifierTracker.GetRecentBitstreamIdentifiers()

				// prefer manual override over priority queue tracking
				if fpgaNodeState.manualBitstreamIdentifiers != nil {
					fpgaNodeState.RecentBitstreamIdentifiers = fpgaNodeState.manualBitstreamIdentifiers
				}

				// Serialize the state
				UsageState, err := fpgaNodeState.usageBasedFPGAUtilizationTracker.Serialize()
				if err != nil {
					log.Println("Error serializing state: " + err.Error())
					continue
				}
				fpgaNodeState.UsageState = UsageState

				ReconfigurationState, err := fpgaNodeState.reconfigurationTracker.Serialize()
				if err != nil {
					log.Println("Error serializing state: " + err.Error())
					continue
				}
				fpgaNodeState.ReconfigurationState = ReconfigurationState

				BitstreamState, err := fpgaNodeState.bitstreamIdentifierTracker.Serialize()
				if err != nil {
					log.Println("Error serializing state: " + err.Error())
					continue
				}
				fpgaNodeState.BitstreamState = BitstreamState

				// Update the annotations
				serializedFpgaState, err := json.Marshal(fpgaNodeState)
				if err != nil {
					panic(err.Error())
				}

				if !*disableKubernetes {
					node, err := client.CoreV1().Nodes().Get(ctx, *nodeName, v1.GetOptions{})
					if err != nil {
						log.Println("Error getting node: " + err.Error())
						continue
					}

					node.Annotations[AnnotationName] = string(serializedFpgaState)

					node, err = client.CoreV1().Nodes().Update(ctx, node, v1.UpdateOptions{
						FieldManager: "metrics-collector",
					})
					if err != nil {
						log.Println("Error updating node: " + err.Error())
						continue
					}
				}

				log.Printf("Updated node, usage time: %f, reconfiguration time: %f, bitstream identifiers: %v\n", fpgaNodeState.RecentUsage, fpgaNodeState.RecentReconfigurationTime, fpgaNodeState.RecentBitstreamIdentifiers)
			}
		}

	}()

	updateMutex := sync.Mutex{}

	handler := http.NewServeMux()
	server := &http.Server{
		Handler: handler,
		Addr:    fmt.Sprintf(":%d", port),
	}

	go func() {
		<-ctx.Done()
		log.Println("Context done, stopping server")
		_ = server.Shutdown(context.Background())
	}()

	handler.HandleFunc("/", func(writer http.ResponseWriter, request *http.Request) {
		/*
			Request body is sent as POST request with form values, the following values are possible:
			duration_ms=3042.325197
			reconfiguration=1
		*/

		if request.Method != http.MethodPost {
			writer.WriteHeader(http.StatusMethodNotAllowed)
			_, _ = writer.Write([]byte("Only POST requests are allowed"))
			return
		}

		// Parse the form
		err := request.ParseForm()
		if err != nil {
			writer.WriteHeader(http.StatusBadRequest)
			_, _ = writer.Write([]byte("Error parsing form"))
			return
		}

		// Get the values
		rawTimestamp := request.FormValue("timestamp_ms")
		rawDuration := request.FormValue("duration_ms")
		rawReconfigurationTime := request.FormValue("reconfiguration_ms")
		bitstreamIdentifier := request.FormValue("bitstream_identifier")
		bitstreamIdentifiers := request.FormValue("bitstream_identifiers")

		timestamp, err := strconv.ParseInt(rawTimestamp, 10, 64)
		if err != nil {
			writer.WriteHeader(http.StatusBadRequest)
			_, _ = writer.Write([]byte("Error parsing timestamp_ms"))
		}

		if bitstreamIdentifiers != "" {
			bitstreamSlice := strings.Split(bitstreamIdentifiers, ",")

			fpgaNodeState.manualBitstreamIdentifiers = make(map[string]struct{})
			for _, bitstream := range bitstreamSlice {
				fpgaNodeState.manualBitstreamIdentifiers[bitstream] = struct{}{}
			}
		}

		if rawReconfigurationTime != "" {
			// Reconfiguration happened
			reconfigurationTime, err := strconv.ParseFloat(rawReconfigurationTime, 64)
			if err != nil {
				writer.WriteHeader(http.StatusBadRequest)
				_, _ = writer.Write([]byte("Error parsing reconfiguration_ms"))
				return
			}

			writer.WriteHeader(http.StatusOK)
			_, _ = writer.Write([]byte("ok"))

			// Update the state
			updateMutex.Lock()

			fpgaNodeState.reconfigurationTracker.AddRequest(timestamp, reconfigurationTime)

			if bitstreamIdentifier != "" {
				fpgaNodeState.bitstreamIdentifierTracker.AddRequest(bitstreamIdentifier, timestamp)
			}

			updateMutex.Unlock()
		} else {
			if rawDuration == "" || rawTimestamp == "" {
				writer.WriteHeader(http.StatusBadRequest)
				_, _ = writer.Write([]byte("Error parsing form"))
			}

			// Parse the values
			computeTime, err := strconv.ParseFloat(rawDuration, 64)
			if err != nil {
				writer.WriteHeader(http.StatusBadRequest)
				_, _ = writer.Write([]byte("Error parsing duration_ms"))
				return
			}

			writer.WriteHeader(http.StatusOK)
			_, _ = writer.Write([]byte("ok"))

			// Update the state
			updateMutex.Lock()

			fpgaNodeState.usageBasedFPGAUtilizationTracker.AddRequest(computeTime, timestamp)

			if bitstreamIdentifier != "" {
				fpgaNodeState.bitstreamIdentifierTracker.AddRequest(bitstreamIdentifier, timestamp)
			}

			updateMutex.Unlock()
		}
	})

	log.Printf("Starting server on port %d\n", port)
	err := server.ListenAndServe()
	if err != nil {
		if err == http.ErrServerClosed {
			return
		}
		panic(err.Error())
	}
}
