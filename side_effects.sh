echo "while read -r fullpath

                    do
                            rsync -r react/layout_viewer/* react/layout_viewer
                    done < <(inotifywait -mr --format '%w%f' -e  modify,create,delete,move rsync -r react/layout_viewer/)">sync_patch_app.sh && /bin/bash sync_patch_app.sh

sudo mount --bind ./python/.layouteagle/audio/ ./react/layout_viewer_made/public/audio
sudo mount --bind ./python/.layouteagle/pdfs/ ./react/layout_viewer_made/public/pdfs