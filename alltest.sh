for file in ./tester/input_*.txt;
do
  echo $file
  python3 main.py < $file
done