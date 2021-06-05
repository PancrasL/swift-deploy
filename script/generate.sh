i=10
while [ $i -le 100 ]
do
    cp ./template/script.js ./script${i}.js
    sed -i 's/{{TARGET}}/'$i'/g' ./script${i}.js
    i=$(expr $i + 10)
done