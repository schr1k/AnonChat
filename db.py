import sqlite3


class DbWorker:
	def __init__(self, database_file):
		self.connection = sqlite3.connect(database_file)
		self.cursor = self.connection.cursor()

	def get_state(self, tg_id: str | int) -> str:
		with self.connection:
			result = self.cursor.execute(
				"SELECT `state` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)).fetchone()
			return result

	def set_state(self, state: str | None, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `state` = ? WHERE `tg_id` = ?",
				(state, tg_id)
			)

	def user_exists(self, tg_id: str | int) -> bool:
		with self.connection:
			result = self.cursor.execute(
				"SELECT * FROM `users` WHERE `tg_id` = ?",
				(tg_id,)).fetchall()
			return bool(len(result))

	def new_user(self, name: str, age: str, sex: str, country: str, city: str, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"INSERT INTO `users` (`name`, `age`, `sex`, `country`, `city`, `tg_id`)"
				"VALUES(?, ?, ?, ?, ?, ?)",
				(name, age, sex, country, city, tg_id)
			)
			return result

	def edit_name(self, name: str, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `name` = ? WHERE `tg_id` = ?",
				(name, tg_id)
			)

	def edit_age(self, age: str, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `age` = ? WHERE `tg_id` = ?",
				(age, tg_id)
			)

	def edit_sex(self, sex: str, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `sex` = ? WHERE `tg_id` = ?",
				(sex, tg_id)
			)

	def edit_country(self, country: str, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `country` = ? WHERE `tg_id` = ?",
				(country, tg_id)
			)

	def edit_city(self, city: str, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `city` = ? WHERE `tg_id` = ?",
				(city, tg_id)
			)

	def edit_op_sex(self, op_sex: str, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `op_sex` = ? WHERE `tg_id` = ?",
				(op_sex, tg_id)
			)

	def edit_vip_ends(self, time: str, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `vip_ends` = ? WHERE `tg_id` = ?",
				(time, tg_id)
			)

	def get_name(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `name` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_age(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `age` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_sex(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `sex` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_country(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `country` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_city(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `city` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_op_sex(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `op_sex` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_notifications(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `notifications` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_vip_ends(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `vip_ends` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_refs(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `refs` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_chats(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `chats` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_messages(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `messages` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_likes(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `likes` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_dislikes(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `dislikes` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_last_connect(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `last_connect` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_points(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `points` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def get_order_id(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT `order_id` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()
			return result

	def search(self, tg_id: str | int) -> str | int:
		with self.connection:
			res = self.cursor.execute(
				"SELECT `tg_id` FROM `queue` WHERE `tg_id` <> ?",
				(tg_id,)
			).fetchone()
			return res

	def search_vip(self, tg_id: str | int, sex: str, op_sex: str) -> str | int:
		with self.connection:
			res = self.cursor.execute(
				"SELECT `tg_id` FROM `queue` WHERE `tg_id` <> ? AND `op_sex` = ? AND (`sex` = ? OR `sex` is null)",
				(tg_id, sex, op_sex)
			).fetchone()
			return res

	def add_to_queue(self, tg_id: str | int, sex: str):
		with self.connection:
			self.cursor.execute(
				"INSERT INTO `queue` (`tg_id`, `sex`, `op_sex`) "
				"VALUES(?, ?, ?)",
				(tg_id, sex, None)
			)

	def add_to_queue_vip(self, tg_id: str | int, sex: str, op_sex: str):
		with self.connection:
			self.cursor.execute(
				"INSERT INTO `queue` (`tg_id`, `sex`, `op_sex`) "
				"VALUES(?, ?, ?)",
				(tg_id, sex, op_sex)
			)

	def delete_from_queue(self, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"DELETE FROM `queue` WHERE `tg_id` = (?)",
				(tg_id,)
			)

	def update_connect_with(self, connect_with: str | int | None, tg_id: str | int):
		if connect_with != tg_id:
			with self.connection:
				self.cursor.execute(
					"UPDATE `users` SET `connect_with` = ? WHERE `tg_id` = ?",
					(connect_with, tg_id)
				)

	def get_connect_with(self, tg_id: str | int) -> str | int:
		with self.connection:
			return self.cursor.execute(
				"SELECT `connect_with` FROM `users` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchone()

	def get_connect_with_self(self, tg_id: str | int) -> str | int:
		with self.connection:
			return self.cursor.execute(
				"SELECT `tg_id` FROM `users` WHERE `connect_with` = ?",
				(tg_id,)
			).fetchone()

	def log_message(self, tg_id: str | int, message):
		with self.connection:
			self.cursor.execute(
				"INSERT INTO `all_messages` (`sender`, `message`) "
				"VALUES (?, ?)",
				(tg_id, message)
			)

	def queue_exists(self, tg_id: str | int):
		with self.connection:
			result = self.cursor.execute(
				"SELECT * FROM `queue` WHERE `tg_id` = ?",
				(tg_id,)
			).fetchall()
			return bool(len(result))

	def count_user(self):
		with self.connection:
			result = self.cursor.execute(
				"SELECT COUNT(*) FROM `users`"
			).fetchone()
			return result[0]

	def edit_refs(self, value: int, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `refs` = `refs` + ? WHERE `tg_id` = ?",
				(value, tg_id)
			)

	def edit_messages(self, value: int, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `messages` = `messages` + ? WHERE `tg_id` = ?",
				(value, tg_id)
			)

	def edit_chats(self, value: int, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `chats` = `chats` + ? WHERE `tg_id` = ?",
				(value, tg_id)
			)

	def edit_likes(self, value: int, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `likes` = `likes` + ? WHERE `tg_id` = ?",
				(value, tg_id)
			)

	def edit_dislikes(self, value: int, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `dislikes` = `dislikes` + ? WHERE `tg_id` = ?",
				(value, tg_id)
			)

	def edit_notifications(self, value: int, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `notifications` = ? WHERE `tg_id` = ?",
				(value, tg_id)
			)

	def edit_points(self, value: int, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `points` = `points` + ? WHERE `tg_id` = ?",
				(value, tg_id)
			)

	def edit_order_id(self, value: int, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `order_id` = `order_id` + ? WHERE `tg_id` = ?",
				(value, tg_id)
			)

	def save_last_connect(self, tg_id: str | int):
		with self.connection:
			self.cursor.execute(
				"UPDATE `users` SET `last_connect` = `connect_with` WHERE `tg_id` = ?",
				(tg_id,)
			)

	def top_messages(self):
		with self.connection:
			return self.cursor.execute(
				"SELECT `name`, `messages` FROM `users` ORDER BY `messages` DESC LIMIT 5"
			).fetchall()

	def top_refs(self):
		with self.connection:
			return self.cursor.execute(
				"SELECT `name`, `refs` FROM `users` ORDER BY `refs` DESC LIMIT 5"
			).fetchall()

	def top_likes(self):
		with self.connection:
			return self.cursor.execute(
				"SELECT `name`, `likes` FROM `users` ORDER BY `likes` DESC LIMIT 5"
			).fetchall()

# a = DbWorker('db.db')
