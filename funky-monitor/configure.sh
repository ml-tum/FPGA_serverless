#!/bin/sh
# Copyright (c) 2015-2017 Contributors as noted in the AUTHORS file
#
# This file is part of Solo5, a unikernel base layer.
#
# Permission to use, copy, modify, and/or distribute this software
# for any purpose with or without fee is hereby granted, provided
# that the above copyright notice and this permission notice appear
# in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

die()
{
    echo "$0: $@" 1>&2
    exit 1
}

cc_maybe_gcc()
{
    # ${CC} -dM -E - </dev/null | grep -Eq '^#define __GNUC__ [4-9]$'
    ${CC} -dM -E - </dev/null | grep -Eq -e '^#define __GNUC__ [4-9]$' -e '^#define __GNUC__ 1[0-9]$'
}

cc_is_clang()
{
    ${CC} -dM -E - </dev/null | grep -Eq '^#define __clang__ 1$'
}

cc_has_pie()
{
    ${CC} -dM -E - </dev/null | grep -Eq '^#define __PIE__ [1-9]$'
}

cc_is_gcc()
{
    cc_maybe_gcc && ! cc_is_clang
}

ld_is_lld()
{
    ${LD} --version 2>&1 | grep -q '^LLD'
}

# Allow external override of CC.
# TODO: This needs further work to provide full support for cross-compiling and
# correctly pass through to ukvm-configure where required.
CC=${CC:-cc}
LD=${LD:-ld}

TARGET=$(${CC} -dumpmachine)
[ $? -ne 0 ] &&
    die "Error running '${CC} -dumpmachine', is your compiler working?"
case ${TARGET} in
    x86_64-*|amd64-*)
	TARGET_ARCH=x86_64
        ;;
    aarch64-*)
	TARGET_ARCH=aarch64
        ;;
    *)
        die "Unsupported compiler target: ${TARGET}"
        ;;
esac

# Host-provided header files are installed here for in-tree builds. OPAM will
# install these to $(OPAM_INCDIR)/host where they will be picked up by
# pkg-config.
HOST_INCDIR=${PWD}/include-host

case $(uname -s) in
    Linux)
        # On Linux/gcc we use -nostdinc and copy all the gcc-provided headers.
        cc_is_gcc || die "Only 'gcc' 4.x+ is supported on Linux"
        CC_INCDIR=$(${CC} -print-file-name=include)
        [ -d "${CC_INCDIR}" ] || die "Cannot determine gcc include directory"
        mkdir -p ${HOST_INCDIR}
        cp -R ${CC_INCDIR}/. ${HOST_INCDIR}

        HOST_CFLAGS="-nostdinc"
        # Recent distributions now default to PIE enabled. Disable it explicitly
        # if that's the case here.
        # XXX: This breaks MirageOS in (at least) the build of mirage-solo5 due
        # to -fno-pie breaking the build of lib/dllmirage-solo5_bindings.so.
        # Keep this disabled until that is resolved.
        # cc_has_pie && HOST_CFLAGS="${HOST_CFLAGS} -fno-pie"
        # Same for the stack protector, no robust way to detect if this is on by
        # default so always disable it.
        HOST_CFLAGS="${HOST_CFLAGS} -fno-stack-protector"
        BUILD_UKVM="yes"
        if [ "${TARGET_ARCH}" = "x86_64" ]; then
            BUILD_VIRTIO="yes"
            BUILD_MUEN="yes"
        else
            BUILD_VIRTIO="no"
            BUILD_MUEN="no"
        fi
        ;;
    FreeBSD)
        # On FreeBSD/clang we use -nostdlibinc which gives us access to the
        # clang-provided headers for compiler instrinsics. We copy the rest
        # (std*.h, float.h and their dependencies) from the host.
        cc_is_clang || die "Only 'clang' is supported on FreeBSD"
        [ "${TARGET_ARCH}" = "x86_64" ] ||
            die "Only 'x86_64' is supported on FreeBSD"
        INCDIR=/usr/include
        SRCS_MACH="machine/_stdint.h machine/_types.h machine/endian.h \
            machine/_limits.h"
        SRCS_SYS="sys/_null.h sys/_stdint.h sys/_types.h sys/cdefs.h \
            sys/endian.h sys/_stdarg.h"
        SRCS_X86="x86/float.h x86/_stdint.h x86/stdarg.h x86/endian.h \
            x86/_types.h x86/_limits.h"
        SRCS="float.h osreldate.h stddef.h stdint.h stdbool.h stdarg.h"

        mkdir -p ${HOST_INCDIR}
        mkdir -p ${HOST_INCDIR}/machine ${HOST_INCDIR}/sys ${HOST_INCDIR}/x86
        for f in ${SRCS_MACH}; do cp -f ${INCDIR}/$f ${HOST_INCDIR}/machine; done
        for f in ${SRCS_SYS}; do cp -f ${INCDIR}/$f ${HOST_INCDIR}/sys; done
        for f in ${SRCS_X86}; do cp -f ${INCDIR}/$f ${HOST_INCDIR}/x86; done
        for f in ${SRCS}; do cp -f ${INCDIR}/$f ${HOST_INCDIR}; done

        HOST_CFLAGS="-nostdlibinc"
        BUILD_UKVM="yes"
        BUILD_VIRTIO="yes"
        BUILD_MUEN="yes"
        ;;
    OpenBSD)
        # On OpenBSD/clang we use -nostdlibinc which gives us access to the
        # clang-provided headers for compiler instrinsics. We copy the rest
        # (std*.h, cdefs.h and their dependencies) from the host.
        cc_is_clang || die "Only 'clang' is supported on OpenBSD"
        [ "${TARGET_ARCH}" = "x86_64" ] ||
            die "Only 'x86_64' is supported on OpenBSD"
        if ! ld_is_lld; then
            LD='/usr/bin/ld.lld'
            echo "using GNU 'ld' is not supported on OpenBSD, falling back to 'ld.lld'"
            [ -e ${LD} ] || die "/usr/bin/ld.lld does not exist"
        fi
        INCDIR=/usr/include
        SRCS_MACH="machine/_float.h machine/endian.h machine/cdefs.h machine/_types.h"
        SRCS_SYS="sys/_null.h sys/cdefs.h sys/_endian.h sys/endian.h sys/_types.h"
        SRCS_AMD64="amd64/_float.h amd64/stdarg.h amd64/endian.h"
        SRCS="float.h stddef.h stdint.h stdbool.h stdarg.h"

        mkdir -p ${HOST_INCDIR}
        mkdir -p ${HOST_INCDIR}/machine ${HOST_INCDIR}/sys ${HOST_INCDIR}/amd64
        for f in ${SRCS_MACH}; do cp -f ${INCDIR}/$f ${HOST_INCDIR}/machine; done
        for f in ${SRCS_SYS}; do cp -f ${INCDIR}/$f ${HOST_INCDIR}/sys; done
        for f in ${SRCS_AMD64}; do cp -f ${INCDIR}/$f ${HOST_INCDIR}/amd64; done
        for f in ${SRCS}; do cp -f ${INCDIR}/$f ${HOST_INCDIR}; done

        HOST_CFLAGS="-fno-pie -fno-stack-protector -nostdlibinc"
        HOST_LDFLAGS="-nopie"
        BUILD_UKVM="yes"
        BUILD_VIRTIO="yes"
        BUILD_MUEN="yes"
        ;;
    *)
        die "Unsupported build OS: $(uname -s)"
        ;;
esac

cat <<EOM >Makeconf
# Generated by configure.sh, using CC=${CC} for target ${TARGET}
BUILD_UKVM=${BUILD_UKVM}
BUILD_VIRTIO=${BUILD_VIRTIO}
BUILD_MUEN=${BUILD_MUEN}
HOST_CFLAGS=${HOST_CFLAGS}
HOST_LDFLAGS=${HOST_LDFLAGS}
TEST_TARGET=${TARGET}
TARGET_ARCH=${TARGET_ARCH}
CC=${CC}
LD=${LD}
EOM
