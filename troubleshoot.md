### IF I2C BUS IS BROKEN
on RPI run the below then sudo reboot
```
sudo modprobe -r i2c-dev
sudo modprobe i2c-dev
```

### IF SSH IS BROKEN
on RPI run the below then sudo reboot
```
rm -rf ~/.vscode-remote
rm -rf ~/.vscode-server
```
