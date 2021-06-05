i=10
while [ $i -le 100 ]
do
    k6 run ./script${i}.js
    i=$(expr $i + 10)
    sleep 3
done