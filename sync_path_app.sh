while read -r fullpath
do
          echo "close_write: $fullpath"
done < <(inotifywait -mr --format '%w%f' -e  modify,create,delete,move ./layout_viewer/)
