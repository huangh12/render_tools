
hdfs dfs -get hdfs://hobot-bigdata/user/he.huang/project/render_tools/pred_data.zip .

unzip pred_data.zip

hdfs dfs -get hdfs://hobot-bigdata/user/he.huang/project/render_tools/orig_video .

python run_this.py