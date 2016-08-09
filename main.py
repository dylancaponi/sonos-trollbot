import time
import ConfigParser

import soco
import requests

settings = {'DESIRED_ZONE': "Office",
            'MAX_VOLUME': 25,
            'LAST_FM_API_KEY': None,
            'tags': None}

blacklists = {'artist': None,
              'title': None}

# look into 
# alarms
# rick rolling
# get queue / remove from queue
# clean queue of blacklist items before they are played
# OR replace them with troll items

# mute when ads are playing
# playing text to speech

# simulate cd skipping with seek back 1 second over and over again randomly - seek(self, timestamp)
# get_current_track_info use position - 1 over and over

# warble with crossfade
# cross_fade(1) # turn on

# alternate treble /bass -10 to 10
# treble(10)
# bass(10)

# party_mode

class Trollbot:

    def __init__(self):
        self.get_config()
        self.set_zone()
        self.main_loop()

    def get_config(self, config_path='config.ini'):
        Config = ConfigParser.ConfigParser()
        try:
            Config.read(config_path)
            self.cfg = dict(Config.items('settings'))
            self.blacklists = dict(Config.items('blacklists'))
        except:
            print 'warning: no config file found. using defaults. tag lookup disabled.'
            self.cfg = settings
            self.blacklists = blacklists

    def set_zone(self):
        # set zone to match desired zone
        sonos_discovery = soco.discover()
        self.sonos = None
        if sonos_discovery:
            while not self.sonos:
                try:
                    self.sonos = [zone for zone in sonos_discovery if zone.player_name == self.cfg['desired_zone']][0]
                except:
                    print 'fail'
                    self.user_select_zone()
        else:
            print 'warning: no zones found. quitting...'
            quit()

    def user_select_zone(self):
        # get user input if no zone name defined
        zone_names = [zone.player_name for zone in soco.discover()]
        print zone_names
        self.cfg['desired_zone'] = raw_input('Which zone would you like to troll?\n')
        if not self.cfg['desired_zone'] in list(zone_names):
            print self.cfg['desired_zone'], 'is not an option'
            self.cfg['desired_zone'] = None

    def main_loop(self):
        last_title = None
        while True:
            # reset volume if max exceeded
            self.reset_volume()

            track = self.sonos.get_current_track_info()
            artist = track['artist']
            title = track['title']

            position = track['position']

            # test
            # self.troll_repeat(position)

            # print self.sonos.is_playing_radio

            # when song changes
            if title != last_title:
                # output song info
                print track['title'], '-', track['artist']

                # check for blacklisted tag
                if self.is_blacklist_tag(artist, title):
                    self.change_music()

                # check for blacklisted title, artist, partial match
                for blacklist in self.blacklists:
                    if track[blacklist].lower() in self.blacklists[blacklist]:
                        self.change_music()

            last_title = title
            time.sleep(3)

    def reset_volume(self):
        current_volume = self.sonos.volume
        if current_volume > self.cfg['max_volume']:
            print 'volume', current_volume, 'exceeds:', self.cfg['max_volume']
            self.sonos.volume = self.cfg['max_volume']
            print 'volume reduced to:', self.cfg['max_volume']

    # simulate cd skipping
    def troll_repeat(self, position, repeats=4, delay=2):
        try:
            for i in range(repeats):
                self.sonos.seek(position)
                time.sleep(delay)
        except:
            'skipping failed, may be playing radio'

    def is_blacklist_tag(self, artist, title):
        # get top tags to check genre
        if self.cfg['last_fm_api_key']:
            last_fm_call = 'http://ws.audioscrobbler.com/2.0/?method=track.gettoptags&artist=' + artist + '&track=' + title + '&api_key=' + self.cfg['last_fm_api_key'] + '&format=json'
            response = requests.get(last_fm_call)
            tags_json = response.json()

            try:
                tags = [tag['name'] for tag in tags_json['toptags']['tag']]
                print tags

                for tag in self.cfg['tags']:
                    if tag in tags:
                        print tag, 'is blacklisted'
                        return True
            except:
                print 'no tags on lastfm'
                pass

    def blacklist_add(self, blacklist_type, value):
        if value not in self.cfg[blacklist_type]:
            self.cfg[blacklist_type].append(value)

    def blacklist_remove(self, blacklist_type, value):
        try:
            self.cfg[blacklist_type].remove(value)
        except:
            pass

    # try to skip, change playlist, mute
    def change_music(self):
        try:
            self.sonos.next()
        except:
            self.sonos.mute()


trollbot = Trollbot()



