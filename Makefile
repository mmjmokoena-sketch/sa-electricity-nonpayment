.PHONY: all data analysis test site demo

all: data analysis test

data:
	python -m src.common.pipeline

analysis:
	python -m src.a_who_pays.run_all

test:
	pytest -q

demo:
	python -m src.a_who_pays.run_all --mode synthetic

site:
	quarto render docs
