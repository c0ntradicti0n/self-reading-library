# Builds the c0ntradiction/pdf2htmlex base image from the patched source:
# https://github.com/c0ntradicti0n/pdf2htmlEX-1

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PDF2HTMLEX_PREFIX=/usr/local
ENV MAKE_PARALLEL="-j4"

# ── Build tools + dev libraries ──────────────────────────────────────────────
RUN apt-get update && apt-get --assume-yes install \
        sudo wget git pkg-config ruby autoconf libtool cmake make gcc g++ \
        dpkg dpkg-dev gettext openjdk-8-jre-headless jq \
        libcairo-dev libpng-dev libjpeg-dev libxml2-dev \
        zlib1g-dev libfreetype6-dev libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# ── Clone the patched pdf2htmlEX-1 repo ─────────────────────────────────────
RUN git clone --depth 1 https://github.com/c0ntradicti0n/pdf2htmlEX-1.git .

# ── Poppler 0.89.0 ───────────────────────────────────────────────────────────
RUN wget -q https://poppler.freedesktop.org/poppler-0.89.0.tar.xz \
    && tar xf poppler-0.89.0.tar.xz \
    && mv poppler-0.89.0 poppler \
    && wget -q https://poppler.freedesktop.org/poppler-data-0.4.9.tar.gz \
    && tar xf poppler-data-0.4.9.tar.gz \
    && mv poppler-data-0.4.9 poppler-data

RUN cd poppler && mkdir build && cd build && cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=$PDF2HTMLEX_PREFIX \
        -DENABLE_UNSTABLE_API_ABI_HEADERS=OFF \
        -DBUILD_GTK_TESTS=OFF \
        -DBUILD_QT5_TESTS=OFF \
        -DBUILD_CPP_TESTS=OFF \
        -DENABLE_SPLASH=ON \
        -DENABLE_UTILS=OFF \
        -DENABLE_CPP=OFF \
        -DENABLE_GLIB=ON \
        -DENABLE_GOBJECT_INTROSPECTION=OFF \
        -DENABLE_GTK_DOC=OFF \
        -DENABLE_QT5=OFF \
        -DENABLE_LIBOPENJPEG=none \
        -DENABLE_CMS=none \
        -DENABLE_DCTDECODER=libjpeg \
        -DENABLE_LIBCURL=OFF \
        -DENABLE_ZLIB=ON \
        -DENABLE_ZLIB_UNCOMPRESS=OFF \
        -DUSE_FLOAT=OFF \
        -DBUILD_SHARED_LIBS=OFF \
        -DRUN_GPERF_IF_PRESENT=OFF \
        -DEXTRA_WARN=OFF \
        -DWITH_JPEG=ON \
        -DWITH_PNG=ON \
        -DWITH_TIFF=OFF \
        -DWITH_NSS3=OFF \
        -DWITH_Cairo=ON \
        .. \
    && make $MAKE_PARALLEL \
    && make install

# Install poppler-data
RUN cd poppler-data && make install \
        prefix=$PDF2HTMLEX_PREFIX \
        datadir=$PDF2HTMLEX_PREFIX/share/pdf2htmlEX

# ── FontForge 20200314 ────────────────────────────────────────────────────────
RUN wget -q https://github.com/fontforge/fontforge/archive/20200314.tar.gz \
    && tar xf 20200314.tar.gz \
    && mv fontforge-20200314 fontforge

RUN cd fontforge && mkdir build && cd build && cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=$PDF2HTMLEX_PREFIX \
        -DBUILD_SHARED_LIBS:BOOL=OFF \
        -DENABLE_GUI:BOOL=OFF \
        -DENABLE_X11:BOOL=OFF \
        -DENABLE_NATIVE_SCRIPTING:BOOL=ON \
        -DENABLE_PYTHON_SCRIPTING:BOOL=OFF \
        -DENABLE_PYTHON_EXTENSION:BOOL=OFF \
        -DENABLE_LIBSPIRO:BOOL=OFF \
        -DENABLE_LIBUNINAMESLIST:BOOL=OFF \
        -DENABLE_LIBGIF:BOOL=OFF \
        -DENABLE_LIBJPEG:BOOL=ON \
        -DENABLE_LIBPNG:BOOL=ON \
        -DENABLE_LIBREADLINE:BOOL=OFF \
        -DENABLE_LIBTIFF:BOOL=OFF \
        -DENABLE_WOFF2:BOOL=OFF \
        -DENABLE_DOCS:BOOL=OFF \
        -DENABLE_CODE_COVERAGE:BOOL=OFF \
        -DENABLE_DEBUG_RAW_POINTS:BOOL=OFF \
        -DENABLE_FONTFORGE_EXTRAS:BOOL=OFF \
        -DENABLE_MAINTAINER_TOOLS:BOOL=OFF \
        -DENABLE_TILE_PATH:BOOL=OFF \
        -DENABLE_WRITE_PFM:BOOL=OFF \
        -DENABLE_SANITIZER:STRING=none \
        -DENABLE_FREETYPE_DEBUGGER:PATH="" \
        -DSPHINX_USE_VENV:BOOL=OFF \
        -DREAL_TYPE:STRING=double \
        -DTHEME:STRING=tango \
        .. \
    && make $MAKE_PARALLEL \
    && make install

# ── pdf2htmlEX (patched source from the cloned repo) ────────────────────────
RUN cd pdf2htmlEX && mkdir build && cd build && cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=$PDF2HTMLEX_PREFIX \
        .. \
    && make $MAKE_PARALLEL \
    && make install

# ── Clean up build artefacts to keep image smaller ──────────────────────────
RUN rm -rf /build

WORKDIR /pdf

