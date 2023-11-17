import time
import board
import neopixel

from image_convertor import convert_image
LED_COUNT = 225

pixels = neopixel.NeoPixel(board.D18, LED_COUNT)

def test_sequence():
	'''Illuminate each LED in turn to check operation'''
	pixels.fill((0, 0, 0))
	for x in range(LED_COUNT):
		pixels[x] = (0, 255, 255)
		time.sleep(0.25)
	for x in range(LED_COUNT):
		pixels[x] = (0, 0, 0)
		time.sleep(0.25)

def display_product(image_path):
	led_values = convert_image(image_path)
	for x in range(LED_COUNT):
		if sum(led_values[x] < 200):
			pixels[x] = led_values[x]
		else:
			pixels[x] = [0,0,0]


if __name__ == '__main__':
	image_path = "disk-image.png"
	paths = ['fan.jpg', 'robot.jpg', 'vacuum.jpg', 'zone.jpg']
	while True:
		for x in paths:
			display_product(f"Solutions/{x}")
			time.sleep(3)


