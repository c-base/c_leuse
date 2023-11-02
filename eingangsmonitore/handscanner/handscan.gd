extends Control

const TOPIC_USER_WHO = "user/who"
const TOPIC_BOARDING = "user/boarding"
const TOPIC_LEAVING = "user/leaving"
const TOPIC_TODAYS_EVENTS = "events/today"
const NO_EVENTS = "Fu:r heute sind leider ceine Events eingetragen, lass dich u:berraschen.\n\n"
const TODAYS_EVENTS = "Heute an Bord:\n\n%s"

const fremdkoerper_flugzeug = "Bitte begeben sie sich in den bereich social engineering."
const fremdkoerper_implantat = "Bionisches Implantat entdeckt."
const fremdkoerper_mate = "Glashaltiges Gebilde im Magen. Bitte begeben sie sich umgehend zur Biowaffenentsorgungsstation auf Ebene 5b."

var broker_url = "tcp://10.0.1.17"
@onready var pfeil = $bottom/pfeil
@onready var handscan = $top/handscan
@onready var handscan_sounds = [$sounds/bioscan, $sounds/handscan, $sounds/grundtonus, $sounds/zellen, $sounds/bakterien, $sounds/success]
@onready var _MainWindow: Window = get_window()

var pfeile = []
var scan_finished = false
var handscan_ready = true
var handscan_state = "ready"
var scan_tween_1
var scan_tween_2
var event_message = NO_EVENTS
var who_message = ""
var who = ""

func _ready():
	ProjectSettings.set_setting("display/window/per_pixel_transparency/allowed", true)
	# _MainWindow.mode = Window.MODE_WINDOWED
	for n in 12:
		var pfeil_clone = pfeil.duplicate()
		pfeil_clone.rotate(deg_to_rad(n*360/12))
		$bottom.add_child(pfeil_clone)
		pfeile.append(pfeil_clone)
	pfeil.queue_free()
	handscan.hide()
	display_events()
	_on_timer_timeout()
	$MQTT.client_id = "handscanner"
	$MQTT.verbose_level = 0
	$MQTT.connect_to_broker(broker_url)

func _on_timer_timeout():
	for n in 12:
		var pfeil_clone = pfeile[n]
		var tween = get_tree().create_tween()
		tween.tween_property(pfeil_clone, "modulate", Color(1, 1, 1, 1), 0.0).set_delay(n/6.0)
		tween.tween_property(pfeil_clone, "modulate", Color(1, 1, 1, 0), 1.0)

func start_handscan():
	if handscan_state != "ready":
		return
	handscan_state = "scanning"
	$top/scanning.show()
	scan_finished = false
	$top/MainText.hide()
	$top/HandPulse.show()
	$top/HandPulse.play()
	$bottom/AuflageLila.show()
	$bottom/scanbalken_left.play()
	$bottom/scanbalken_right.play()
	var tween_left = get_tree().create_tween()
	tween_left.tween_property($bottom/scanbalken_left, "position", Vector2(-8, 0), 0.0)
	tween_left.tween_property($bottom/scanbalken_left, "position", Vector2(-8, 550), 5.0)
	tween_left.tween_property($bottom/scanbalken_left, "position", Vector2(-8, 0), 5.0)
	var tween_right = get_tree().create_tween()
	tween_right.tween_property($bottom/scanbalken_right, "position", Vector2(729, 0), 0.0)
	tween_right.tween_property($bottom/scanbalken_right, "position", Vector2(729, 550), 5.0)
	tween_right.tween_property($bottom/scanbalken_right, "position", Vector2(729, 0), 5.0)
	$sounds/bioscan.play()
	for n in 12:
		pfeile[n].hide()
	scan_part1(1.0, 0.1)

func stop_handscan():
	if handscan_state not in "scanning":
		return
	if not scan_finished:
		cleanup()
		$sounds/beep_abort.play()
		$bottom/AuflageRot.show()
		$top/vorgang_abgebrochen.show()
		handscan_state = "aborted"
		
func cleanup():
	stop_handscan_sounds()
	$bottom/AuflageLila.hide()
	$bottom/AuflageGruen.hide()
	$bottom/AuflageRot.hide()
	$top/vorgang_abgebrochen.hide()
	$bottom/AuflageGruenLogin.hide()
	$top/GreenScreen.hide()
	$top/HandPulse.stop()
	$top/koerperscan.stop()
	$top/koerperscan.hide()
	$top/fremdkoerper.hide()
	$top/Bodyscan.hide()
	handscan.hide()
	handscan.stop()
	$top/scanning.hide()
	$bottom/scanbalken_left.stop()
	$bottom/scanbalken_right.stop()
	display_events()
	$top/MainText.show()
	scan_part1(0.0, 0.0)
	scan_part2(0.0, 0.0)

func display_events():
	$top/MainText.text = event_message + get_motivation_message()

func stop_handscan_sounds():
	for sound in handscan_sounds:
		sound.stop()

func _unhandled_input(event):
	if event is InputEventKey:
		if event.pressed and event.keycode == KEY_ESCAPE:
			get_tree().quit()

func _on_control_gui_input(event):
	if (event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT) or event is InputEventScreenTouch:
		if event.pressed:
			start_handscan()
		else:
			stop_handscan()

func _on_scanbalken_finished():
	handscan.stop()
	handscan.hide()
	$top/koerperscan.stop()
	$top/koerperscan.hide()
	$top/scanning.hide()
	scan_part2(0.0, 0.0)
	var rng = RandomNumberGenerator.new()
	var result = rng.randi_range(0, 4)
	if result < 2:
		$bottom/AuflageLila.hide()
		$bottom/AuflageGruen.show()
		$top/GreenScreen.show()
		$sounds/willkommen.play()
		handscan_state = "success"
	else:
		if result == 2:
			$top/fremdkoerper/text.text = fremdkoerper_flugzeug
			$top/fremdkoerper/IconFlugzeug.show()
			$top/fremdkoerper/IconImplantat.hide()
			$top/fremdkoerper/IconMate.hide()
		elif result == 3:
			$top/fremdkoerper/text.text = fremdkoerper_implantat
			$top/fremdkoerper/IconFlugzeug.hide()
			$top/fremdkoerper/IconImplantat.show()
			$top/fremdkoerper/IconMate.hide()
		elif result == 4:
			$top/fremdkoerper/text.text = fremdkoerper_mate
			$top/fremdkoerper/IconFlugzeug.hide()
			$top/fremdkoerper/IconImplantat.hide()
			$top/fremdkoerper/IconMate.show()
		$top/fremdkoerper.show()
		$top/Bodyscan.show()
		$sounds/failure.play()
		$bottom/AuflageLila.hide()
		$bottom/AuflageRot.show()
		handscan_state = "failure"
	scan_finished = true

func _on_bioscan_finished():
	$top/HandPulse.hide()
	$top/HandPulse.stop()
	handscan.show()
	handscan.play()
	$sounds/handscan.play()
	
func _on_handscan_sound_finished():
	$sounds/bitte_stehenbleiben.play()
	$top/koerperscan.show()
	$top/koerperscan.play()
	scan_part1(0.0, 0.0)
	scan_part2(1.0, 0.2)

func _on_bitte_stehenbleiben_finished():
	$sounds/grundtonus.play()
	
func _on_grundtonus_finished():
	$sounds/zellen.play()

func _on_zellen_finished():
	$sounds/bakterien.play()

func _on_bakterien_finished():
	pass

func _on_beep_abort_finished():
	$sounds/nicht_identifiziert.play()

func _on_nicht_identifiziert_finished():
	reset()

func _on_willkommen_finished():
	reset()

func _on_failure_finished():
	await get_tree().create_timer(5).timeout
	reset()

func reset():
	cleanup()
	for n in 12:
		pfeile[n].show()
	handscan_state = "ready"

func get_motivation_message():
	return "We are excellent to each other!\n\n"
	
func _on_mqtt_received_message(topic, message):
	var json = JSON.new()
	json.parse(message)
	if topic == TOPIC_BOARDING:
		boarding_message(json.data['user'])
	if topic == TOPIC_USER_WHO:
		who = json.data
		var text = ""
		if 'available' in who and len(who['available']) > 0:
			text += "An Bord: %s\n\n" % ", ".join(who['available'])
		if 'eta' in who and len(who['eta']) > 0:
			var etalist = []
			for key in who['eta'].keys().sorted():
				etalist += ['%s [%s]' % [key, who['eta'][key]]]
			text += "ETA: %s\n\n" % ", ".join(etalist)
		who_message = text
	if topic == TOPIC_LEAVING:
		leaving_message(json.data)
	if topic == TOPIC_TODAYS_EVENTS:
		if len(json.data) > 0:
			event_message = TODAYS_EVENTS % "\n".join(json.data)
		else:
			event_message = NO_EVENTS
		display_events()

func boarding_message(user):
	# if handscan_state != "ready":
	# 	await get_tree().create_timer(2).timeout
	# 	return boarding_message(user)
	$sounds/login.play()
	$bottom/AuflageGruenLogin.show()
	message("Hallo " + user + ", willcommen auf der c-base!\n\n" + event_message + "\n\n" + who_message)

func leaving_message(data):
	$sounds/logout.play()
	$bottom/AuflageGruenLogin.show()
	var ceitloch = 4254
	message("Guten Heimflug %s!\n\nDu warst dieses mal fu:r %d secunden im ceitloch. dabei hast du circa %d Liter Sauerstoff umgesetzt und ungefa:hr %d mal geblinzelt." % [data['user'], ceitloch, ceitloch * 0.4, ceitloch / 5])

func message(msg, duration=10):
	$top/MainText.text = msg
	for n in 12:
		pfeile[n].hide()
	$ResetTimer.start(duration)

func _on_mqtt_broker_connected():
	$MQTT.subscribe("user/+")
	$MQTT.subscribe(TOPIC_TODAYS_EVENTS)

func _on_reset_timer_timeout():
	reset()

func scan_part1(alpha, delay):
	if scan_tween_1:
		scan_tween_1.kill()
	scan_tween_1 = get_tree().create_tween()
	scan_tween_1.tween_property($top/moleculare_structur/Panel1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/Panel1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/lebensform_hercunft/Panel1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/moleculare_structur/Panel2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/Panel2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/lebensform_hercunft/Panel2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/moleculare_structur/Panel2/Molekuel, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/Panel2/Helix, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/lebensform_hercunft/Panel2/Welt, "modulate", Color(1, 1, 1, alpha), delay)
	
	scan_tween_1.tween_property($top/moleculare_structur/title, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/moleculare_structur/zeile1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/moleculare_structur/zeile2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/moleculare_structur/zeile3, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/moleculare_structur/zeile4, "modulate", Color(1, 1, 1, alpha), delay)

	scan_tween_1.tween_property($top/genetische_transcription/title, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/zeile1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/zeile2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/zeile3, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/zeile4, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/zeile5, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/genetische_transcription/zeile6, "modulate", Color(1, 1, 1, alpha), delay)

	scan_tween_1.tween_property($top/lebensform_hercunft/title, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/lebensform_hercunft/zeile1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/lebensform_hercunft/zeile2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/lebensform_hercunft/zeile3, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/lebensform_hercunft/zeile4, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_1.tween_property($top/lebensform_hercunft/zeile5, "modulate", Color(1, 1, 1, alpha), delay)
	
func scan_part2(alpha, delay):
	if scan_tween_2:
		scan_tween_2.kill()
	scan_tween_2 = get_tree().create_tween()
	scan_tween_2.tween_property($top/grundtonus/Panel1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/zellen/Panel1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/gehirn/Panel1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/grundtonus/Panel2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/zellen/Panel2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/gehirn/Panel2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/grundtonus/Panel2/Grundtonus, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/zellen/Panel2/Zellen, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/gehirn/Panel2/Gehirn, "modulate", Color(1, 1, 1, alpha), delay)
	
	scan_tween_2.tween_property($top/grundtonus/title, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/grundtonus/zeile1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/grundtonus/zeile2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/grundtonus/zeile3, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/grundtonus/zeile4, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/grundtonus/zeile5, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/grundtonus/zeile6, "modulate", Color(1, 1, 1, alpha), delay)

	scan_tween_2.tween_property($top/zellen/title, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/zellen/zeile1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/zellen/zeile2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/zellen/zeile3, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/zellen/zeile4, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/zellen/zeile5, "modulate", Color(1, 1, 1, alpha), delay)

	scan_tween_2.tween_property($top/gehirn/title, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/gehirn/zeile1, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/gehirn/zeile2, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/gehirn/zeile3, "modulate", Color(1, 1, 1, alpha), delay)
	scan_tween_2.tween_property($top/gehirn/zeile4, "modulate", Color(1, 1, 1, alpha), delay)
