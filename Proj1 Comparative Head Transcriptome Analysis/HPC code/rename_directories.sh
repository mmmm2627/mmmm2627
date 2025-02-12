#!/bin/bash

for oldname in SRR*; do
    IFS= read -r newname || break
    mv --no-clobber -- "$oldname" "$newname"
done < new_name.txt

echo "Directory renaming completed."
