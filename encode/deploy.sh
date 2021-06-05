kubeless function deploy hello --from-file hello.py --handler hello.hello --runtime python3.6 --dependencies requirements.txt
kubectl scale deploy --replicas=3 hello