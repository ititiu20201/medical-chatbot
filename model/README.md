Run code:

1. Open and connect FortiClient:
   Username: hvusynh
   
   Password: ...
   
3. Open run terminal:
4. 
   2.1: connect to server:
   
   Username: ssh hvusynh@192.168.100.130
   
   Password: 
   
   2.2: install remote explorer in VSCode
   
   connect to ssh hvusynh@192.168.100.130
   
   password: 
   
   sau khi kết nối được ssh thì sẽ xuất hiện project
   
   mở terminal và run:

- conda activate torch-env #connect to conda environment
- cd medical-chatbot
- export PYTHONPATH=~/medical-chatbot:$PYTHONPATH
- python model/process_data.py #processing data
- python model/train_model.py
