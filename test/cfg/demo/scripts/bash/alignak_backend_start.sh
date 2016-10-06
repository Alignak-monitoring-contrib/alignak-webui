echo "Start Alignak backend..."
screen -d -S alignak_backend -m bash -c "cd /root/git/alignak-backend && ./bin/run.sh"
sleep 1
