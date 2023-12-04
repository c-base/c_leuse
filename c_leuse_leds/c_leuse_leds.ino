#include <FastLED.h>
#include <simpleRPC.h>
 
FASTLED_USING_NAMESPACE
 
// FastLED "100-lines-of-code" demo reel, showing just a few 
// of the kinds of animation patterns you can quickly and easily 
// compose using FastLED.  
//
// This example also shows one easy way to define multiple 
// animations patterns and have them automatically rotate.
//
// -Mark Kriegsman, December 2014
 
 
#define DATA_PIN    51
//#define CLK_PIN   4
#define LED_TYPE    WS2801
#define COLOR_ORDER BGR
#define NUM_LEDS    516
CRGB leds[NUM_LEDS];

// #define NUM_STRIPS 4
// #define NUM_LEDS_PER_STRIP 129
// CRGB leds[NUM_STRIPS][NUM_LEDS_PER_STRIP];
 
#define BRIGHTNESS         255
#define FRAMES_PER_SECOND  120
 
uint8_t gCurrentPatternNumber = 0; // Index number of which pattern is current
uint8_t gHue = 0; // rotating "base color" used by many of the patterns
uint16_t gPos = 0;
uint16_t gSpeed = 8;


class LEDStripSegment{
  private:
    int num_leds;
    CRGB* leds;
    CRGB* arrayPointer;
    int position = 0;
    int stepSize = 2;
    bool reversed = false;
    bool forward = true; 
    
  public:
    LEDStripSegment(int num_leds, CRGB* arrayPointer, bool reversed) {
      this->num_leds = num_leds;
      this->leds = new CRGB[num_leds];
      this->arrayPointer = arrayPointer;
      this->setPattern1();
      this->reversed = reversed;
    }
    void renderFrame2() {
      fill_solid( this->arrayPointer, (int) this->num_leds/4, CRGB::Black);
      fill_solid( this->arrayPointer + (int) this->num_leds/4, (int) this->num_leds/4, CRGB::Green);
      fill_solid( this->arrayPointer + (int) this->num_leds/2, (int) this->num_leds/4, CRGB::Black);
      fill_solid( this->arrayPointer + (int) 3*this->num_leds/4, (int) this->num_leds/4, CRGB::Red);
    }
    void setPatternTest(CRGB color){
      fill_solid( this->leds, this->num_leds, color);
    }
    void setPattern1(CRGB color){
      fill_solid( this->leds, (int) this->num_leds/4, CRGB::Black);
      fill_solid( this->leds + (int) this->num_leds/4, (int) this->num_leds/4, color);
      fill_solid( this->leds + (int) this->num_leds/2, (int) this->num_leds/4, CRGB::Black);
      fill_solid( this->leds + (int) 3*this->num_leds/4, (int) this->num_leds/4, color);
    }
    void setPattern1(){
      fill_solid( this->leds, (int) this->num_leds/4, CRGB::Black);
      fill_solid( this->leds + (int) this->num_leds/4, (int) this->num_leds/4, CHSV( gHue, 255, 192));
      fill_solid( this->leds + (int) 2*this->num_leds/4, (int) this->num_leds/4, CRGB::Black);
      fill_solid( this->leds + (int) 3*this->num_leds/4, (int) this->num_leds/4, CHSV( gHue, 255, 192));
    }
    void step(){
      this->move();
      this->renderFrame();
    }
    void renderFrame() {
      if (this->reversed) {
        for (int i=0; i < this->num_leds; i++) {
          this->arrayPointer[i] = this->leds[(i+this->position) % this->num_leds];
        }  
      } else {
        for (int i=0; i < this->num_leds; i++) {
          this->arrayPointer[this->num_leds - i] = this->leds[(i+this->position) % this->num_leds];
        }          
      }
    }
    void move() {
      position = (position + this->stepSize % this->num_leds);
      if (position < 0) {
        position = this->num_leds - position;
      }
    }
};

class LEDStrip{
    private:
      LEDStripSegment segments[];
      int nrOfSegments;
    public:
      LEDStrip(int nrOfSegments) {
        this->nrOfSegments = nrOfSegments;
        //this->segments = new LEDStripSegment[nrOfSegments];
      }
      void addStrip(int id, LEDStripSegment segment) {
        if (id < this->nrOfSegments) {
          this->segments[id] = segment;
        }
      }
      void setPattern1(CRGB color){
        for (int i=0; i<this->nrOfSegments; i++) {
          this->segments[i].setPattern1(color);
        }
      }
      void setPattern1(){
        for (int i=0; i<this->nrOfSegments; i++) {
          this->segments[i].setPattern1();
        }
      }
      void step(){
        for (int i=0; i<this->nrOfSegments; i++) {
          this->segments[i].step();
        }
      }
};

LEDStrip strip = LEDStrip(4);

LEDStripSegment strip1 = LEDStripSegment(127, leds, true);
LEDStripSegment strip2 = LEDStripSegment(129, leds+127, false);
LEDStripSegment strip3 = LEDStripSegment(128, leds+255, true);
LEDStripSegment strip4 = LEDStripSegment(129, leds+384, false);

/*
strip.addStrip(0, strip1);
strip.addStrip(1, strip2);
strip.addStrip(2, strip3);
strip.addStrip(3, strip4);
*/
/*
void setPattern(int pattern_number) {
 gCurrentPatternNumber = pattern_number;
}
*/

void setPattern(char* pattern_name) {
  FastLED.setBrightness(BRIGHTNESS);
  int pattern_number = 0;
  if (strcmp(pattern_name, "off") == 0) {
    pattern_number = 1;
  } else if (strcmp(pattern_name, "notbeleuchtung") == 0) {
    pattern_number = 2;
  } else if (strcmp(pattern_name, "scanning") == 0) {
    pattern_number = 3;
  } else if (strcmp(pattern_name, "success") == 0) {
    pattern_number = 4;
  } else if (strcmp(pattern_name, "failure") == 0) {
    pattern_number = 5;
  }
  gCurrentPatternNumber = pattern_number;
}

void setup() {
  // delay(3000); // 3 second delay for recovery
  Serial.begin(9600);

  // tell FastLED about the LED strip configuration
  // FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.addLeds<WS2801,COLOR_ORDER>(leds, NUM_LEDS);
  //FastLED.addLeds<LED_TYPE,DATA_PIN,CLK_PIN,COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
 
  // set master brightness control
  FastLED.setBrightness(BRIGHTNESS);
}

// List of patterns to cycle through.  Each is defined as a separate function below.
typedef void (*SimplePatternList[])();
SimplePatternList gPatterns = { rainbow, off, notbeleuchtung, scanning, success, failure, oopStrip, wuerstchen, rainbow, rainbowWithGlitter, confetti, sinelon, juggle, bpm };
// SimplePatternList gPatternsRotation = {juggle, rainbow, rainbowWithGlitter, confetti, sinelon, juggle, bpm}

void loop()
{
  interface(
    Serial,
    setPattern, "Set FastLED pattern");
  // Call the current pattern function once, updating the 'leds' array
  gPatterns[gCurrentPatternNumber]();
 
  // send the 'leds' array out to the actual LED strip
  FastLED.show();  
  // insert a delay to keep the framerate modest
  FastLED.delay(1000/FRAMES_PER_SECOND); 
 
  // do some periodic updates
  EVERY_N_MILLISECONDS( 20 ) { 
    gHue++;
    gPos = (gPos + gSpeed) % NUM_LEDS;
  } // slowly cycle the "base color" through the rainbow
  EVERY_N_MILLISECONDS( 20 ) {  }
  // EVERY_N_SECONDS( 10 ) { nextPattern(); } // change patterns periodically
}
 
#define ARRAY_SIZE(A) (sizeof(A) / sizeof((A)[0]))
 
void nextPattern()  
{
  // add one to the current pattern number, and wrap around at the end
  gCurrentPatternNumber = (gCurrentPatternNumber + 1) % ARRAY_SIZE( gPatterns);
}

void off()
{
  fill_solid( leds, NUM_LEDS, CRGB::Black);
}

void rainbow() 
{
  // FastLED's built-in rainbow generator
  fill_rainbow( leds, NUM_LEDS, gHue, 1);
}
 
void rainbowWithGlitter() 
{
  // built-in FastLED rainbow, plus some random sparkly glitter
  rainbow();
  addGlitter(80);
}
 
void addGlitter( fract8 chanceOfGlitter) 
{
  if( random8() < chanceOfGlitter) {
    leds[ random16(NUM_LEDS) ] += CRGB::White;
  }
}
 
void confetti() 
{
  // random colored speckles that blink in and fade smoothly
  fadeToBlackBy( leds, NUM_LEDS, 10);
  int pos = random16(NUM_LEDS);
  leds[pos] += CHSV( gHue + random8(64), 200, 255);
}
 
void sinelon()
{
  // a colored dot sweeping back and forth, with fading trails
  fadeToBlackBy( leds, NUM_LEDS, 20);
  int pos = beatsin16( 13, 0, NUM_LEDS-1 );
  leds[pos] += CHSV( gHue, 255, 192);
}
 
void bpm()
{
  // colored stripes pulsing at a defined Beats-Per-Minute (BPM)
  uint8_t BeatsPerMinute = 62;
  CRGBPalette16 palette = PartyColors_p;
  uint8_t beat = beatsin8( BeatsPerMinute, 64, 255);
  for( int i = 0; i < NUM_LEDS; i++) { //9948
    leds[i] = ColorFromPalette(palette, gHue+(i*2), beat-gHue+(i*10));
  }
}
 
void juggle() {
  // eight colored dots, weaving in and out of sync with each other
  fadeToBlackBy( leds, NUM_LEDS, 20);
  uint8_t dothue = 0;
  for( int i = 0; i < 8; i++) {
    leds[beatsin16( i+7, 0, NUM_LEDS-1 )] |= CHSV(dothue, 200, 255);
    dothue += 32;
  }
}

void wuerstchen() {
  for(int i = 0; i < NUM_LEDS; i++) {
    if (i % 64 < 32) {
      leds[i] = CHSV(gHue, 200, 255);
    } else {
      leds[i] = CRGB::Black;
    }
  }
}

void notbeleuchtung() {
  FastLED.setBrightness(10);
  for(int i = 0; i < NUM_LEDS; i++) {
    if (i % 64 < 32) {
      leds[i] = CRGB::Yellow;
    } else {
      leds[i] = CRGB::Black;
    }
  }
}

void success_new() {
  strip.setPattern1(CRGB::Green);
  // strip.step();
}

void success() {
  strip1.setPattern1(CRGB::Green);
  strip2.setPattern1(CRGB::Green);
  strip3.setPattern1(CRGB::Green);
  strip4.setPattern1(CRGB::Green);
  oopStrip();
} 

void failure() {
  // strip.setPattern1(CRGB::Red);
  // strip.step();
  strip1.setPattern1(CRGB::Red);
  strip2.setPattern1(CRGB::Red);
  strip3.setPattern1(CRGB::Red);
  strip4.setPattern1(CRGB::Red);
  oopStrip();
}

void scanning() {
  fadeToBlackBy( leds, NUM_LEDS, 50);
  // fill_solid( leds, NUM_LEDS, CRGB::Black);
  fill_solid( leds + gPos, 2, CRGB::Blue);
}

void test() {
  strip1.setPatternTest(CRGB::Black);
  strip2.setPatternTest(CRGB::Black);
  strip3.setPatternTest(CRGB::Green);
  strip4.setPatternTest(CRGB::Black);
  oopStrip();
} 

void oopStrip() {
  strip1.step();
  strip2.step();
  strip3.step();
  strip4.step();
}