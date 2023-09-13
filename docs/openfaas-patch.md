
# Patch OpenFaas/faas-netes
Go to file `pkg/k8s/profiles.go` and find the function `ApplyProfile(...)`
Add this code:
`
if profile.RuntimeClassName != nil {
  deployment.Spec.Template.Spec.RuntimeClassName = profile.RuntimeClassName
}
`
Build the image and deploy it to a repo.
Such an image is already available in my private repo at docker.io/ccgroup47/myrepo:faas-netes-rtc
