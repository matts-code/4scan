import basc_py4chan
from collections import Counter
import re


def output(post_list):
	for post_num in post_list:
		try:
			thread = basc_py4chan.get_boards(post_num[0], https=True)[0].get_thread(post_num[1])
			for post in thread.all_posts:
				if post.post_id == post_num[2]:
					print()
					print("*"*80)
					print(post.url)
					print(post.text_comment)
		except Exception as exc:
			print(str(exc))


def search(query, names_of_boards):
	boards = basc_py4chan.get_boards(names_of_boards, https=True)
	for i, board in enumerate(boards):
		print("Searching Board: {0}, ({1}/{2})".format(board.name, i+1, len(boards)))
		thread_ids = board.get_all_thread_ids()
		for thread in board.get_all_threads():
			try:
				b, t = board.name, thread.id				
				for post in thread.all_posts:
					if query in " ".join(word for word in post.text_comment.lower().split() if not word.startswith(">>")):
						post_num = [(b, t, post.post_id)]
						output(post_num)

			except Exception as exc:
		 		print(str(exc))


def find_greentext(names_of_boards):
	boards = basc_py4chan.get_boards(names_of_boards, https=True)
	for i, board in enumerate(boards):
		print("Searching Board: {0}, ({1}/{2})".format(board.name, i+1, len(boards)))
		thread_ids = board.get_all_thread_ids()
		for thread in board.get_all_threads():
			try:
				b, t = board.name, thread.id				
				for post in thread.all_posts:
					lines = post.text_comment.splitlines()
					green_count = sum(1 for line in lines if line.startswith(">") and not line.startswith(">>"))
					if (green_count >= 5) and (green_count / len(lines) >= .5):
						post_num = [(b, t, post.post_id)]
						output(post_num)

			except Exception as exc:
		 		print(str(exc))


def scan(number_of_posts, names_of_boards):
	selected_boards = basc_py4chan.get_boards(names_of_boards, https=True)
	min_count = 0
	reply_counter = Counter()
	for i, board in enumerate(selected_boards):
		print("Scanning Board: {0}, ({1}/{2})".format(board.name, i+1, len(selected_boards)))
		thread_ids = board.get_all_thread_ids()
		for thread in board.get_all_threads():
			try:
				if len(thread.all_posts) >= min_count:
					b, t = board.name, thread.id
					for post in thread.all_posts:
						post_nums = set(re.compile(r'(>>)(\d{5,9})').findall(post.text_comment))
						clean_ids = ((b, t, int(post_num[1])) for post_num in post_nums if int(post_num[1]) not in thread_ids)
						reply_counter += Counter(clean_ids)

					if len(reply_counter) > number_of_posts:
						reply_counter = Counter(dict(reply_counter.most_common(number_of_posts)))
						min_count = reply_counter.most_common(number_of_posts)[-1][1] 
			except Exception as exc:
		 		print(str(exc))

	top_posts = [(*num[0], num[1]) for num in reply_counter.most_common(number_of_posts)]
	output(top_posts)


def board_menu(board_list):
	board_list = [" - ".join([b.name, b.title]) for b in board_list]
	board_list.sort()

	bstring = " "
	for i, board in enumerate(board_list):
		if i % 2 == 0:
			bstring = bstring + "\n" + board
		else:
			offset = 40 - len(board_list[i-1])
			off = " " * offset
			bstring = bstring + off + board

	print("*"*80)
	print(bstring)


def main():
	try:
		board_list = basc_py4chan.get_all_boards(https=True)
	except Exception:
		print("CONNECTION ERROR")
		return

	print("\n4SCAN - The 4chan scanner\n")
	print("""1 - Scan for the "best" posts""")
	print("2 - Scan for greentext")
	print("3 - Scan for a word\n")

	option = input("Choose your option:")

	board_menu(board_list)

	board_names = input("\nChoose your boards:")
	board_names = board_names.split(",")
	board_names = list(map(str.strip, board_names))
	print(board_names)

	if option == "1":
		n = input("How many posts do you want?")
		n = int(n)
		scan(n, board_names)

	elif option == "2":
		find_greentext(board_names)

	elif option == "3":
		word = input("Enter the word you're searching for:")
		search(word, board_names)

if __name__ == "__main__":
	main()
