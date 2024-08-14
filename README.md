# pca-tools
A collection of tools for Oracle's Private Cloud Appliance


## send_bundle

This is a simple shell script that simplifies the process of uploading bundle files (any file is supported) to MOS. Installation is easy, just download it to your PCA MN and run it.


### How to install
```
# mkdir -p /nfs/shared_storage/tools/
# mv send_bundle.sh /nfs/shared_storage/tools/send_bundle.sh
# chmod a+x /nfs/shared_storage/tools/send_bundle.sh
```

### How to run
```
# cd /nfs/shared_storage/support_bundles
../tools/send_bundle.sh ./3-37582104811_pca-support-bundle_20240814T043429658.tar.gz
```


## ssh_wrapper

One of the difficulties of using SSH with PCA is that if / when the master MN changes, the SSH client complains about the host key changing. So I wrote a SSH wrapper script that prompts to delete the host key and re-tries the connection.

### How to install
```
# mkdir -p ~/bin/
# mv sssh.sh ~/bin/
```

### How to use
```
# alias ssh="~/bin/sssh.sh"
# ssh <some host name as usual>
```
