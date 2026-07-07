# ctxconflict frontier (regenerate with tools/analyze.py)
#
# control_correct: model answered parametrically correct with no context.
# override: among control-correct items, fraction that flip to the false
# context answer under the condition. Conditioned on control-correct to
# avoid the 'never knew it' confound.

model qwen1.5b control_correct 22/24 famous_control_correct 11/12
model qwen1.5b condition plain override 4/22 rate 0.1818
model qwen1.5b condition plain tier famous override 1/11 rate 0.0909
model qwen1.5b condition plain tier obscure override 3/11 rate 0.2727
model qwen1.5b condition emphatic override 17/22 rate 0.7727
model qwen1.5b condition emphatic tier famous override 6/11 rate 0.5455
model qwen1.5b condition emphatic tier obscure override 11/11 rate 1.0000
model qwen0.5b control_correct 19/24 famous_control_correct 11/12
model qwen0.5b condition plain override 5/19 rate 0.2632
model qwen0.5b condition plain tier famous override 3/11 rate 0.2727
model qwen0.5b condition plain tier obscure override 2/8 rate 0.2500
model qwen0.5b condition emphatic override 19/19 rate 1.0000
model qwen0.5b condition emphatic tier famous override 11/11 rate 1.0000
model qwen0.5b condition emphatic tier obscure override 8/8 rate 1.0000
