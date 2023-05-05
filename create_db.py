import sqlite3

try:
	connection = sqlite3.connect("db.db")
	connection.execute(
		"create table users (`id` integer primary key autoincrement, `state` varchar(20), `name` varchar(20), `age` varchar(3), `sex` varchar(10), `country` varchar(20), `city` varchar(20), `op_sex` varchar(10), `tg_id` varchar(25), `connect_with` varchar(20), `last_connect` varchar(20), `chats` int default 0, `messages` int default 0, `likes` int default 0, `dislikes` int default 0, `vip_ends` varchar(30), `refs` int default 0, `points` int default 0, `notifications` int default 1, `order_id` int default 0)")
	connection.execute("create table all_messages (`sender` varchar(20), `message` varchar(30))")
	connection.execute("create table queue (`tg_id` varchar(15), `sex` varchar(6), `op_sex` varchar(6))")
except Exception as e:
	print(e)
