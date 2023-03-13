while read -r fullpath
            
                    do
                            rsync -r ../react/layout_viewer/* ../react/layout_viewer_made
                    done < <(inotifywait -mr --format '%w%f' -e  modify,create,delete,move ../react/layout_viewer/)
