mkdir -p /usr/share/storage-manager/
cp -r src /usr/share/storage-manager/src
cp main.py /usr/share/storage-manager/main.py
cp app/storage-manager.desktop /usr/share/applications/storage-manager.desktop
echo "python3 /usr/share/storage-manager/main.py" > /bin/storage-manager
chmod +x /bin/storage-manager