clean:
	rm -f output*.mp4

run: clean
	.venv/bin/python autocropper.py