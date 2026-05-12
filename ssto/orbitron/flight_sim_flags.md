
Usage: fgfs [ option ... ]

General Options:
   --help, -h                   Show the most relevant command line options
   --launcher[={1|0}]           Enable/Disable GUI launcher
   --verbose, -v                Show all command line options when combined
                                with --help or -h
   --version[={1|0}]            Enable/Disable display the current FlightGear
                                version
   --fg-root=path               Specify the root data path
   --fg-scenery=path            Specify the scenery path(s);
                                Defaults to $FG_ROOT/Scenery
   --fg-aircraft=path           Specify additional aircraft directory path(s)
                                (alternatively, you can use --aircraft-dir to
                                target a specific aircraft in a given
                                directory)
   --data=path                  Specify an additional base data directory
                                (FGData), before the $FG_ROOT directory
   --addon=path                 Specify a path to addon;
                                multiple instances can be used
   --download-dir=path          Base directory to use for aircraft and scenery
                                downloads (the TerraSync scenery directory may
                                be specifically set with --terrasync-dir)
   --language=code              Select the language for this session
   --load-tape={name|url}       Load recording of earlier FlightGear session.
                                For <name>, if <name> ends with .fgdata it is
                                treated as the local path of the recording
                                file; otherwise we form the local path by
                                prepending <name> with the tape directory and
                                appending ".fgtape". For <url> (starting with
                                http:// or https://) we download the remote
                                recording (which must be a Continuous
                                recording) in the background to a url-dependent
                                filename while replaying it; if the
                                url-dependent filename already exists it is
                                assumed to be a truncated download and we only
                                download any remaining data.

   --load-tape-create-video[={1|0}]
                                Enable/Disable encode video while replaying
                                tape specified by --load-tape
   --load-tape-fixed-dt=value   Set fixed-dt mode while replaying tape
                                specified by --load-tape
   --restore-defaults[={1|0}]   Enable/Disable resetting all user settings to
                                their defaults (rendering options etc.)
   --save-on-exit[={1|0}]       Enable/Disable saving preferences at program
                                exit
   --browser-app=path           Specify path to your web browser
   --prop:[type:]name=value     Set property <name> to <value>. <type> can be
                                one of string, double, float, long, int, or
                                bool
   --prop:browser=property      After starting the simulator, immediately open
                                the properties dialog with the given property
   --config=path                Load additional properties from path
   --no-default-config[={1|0}]  Enable/Disable not loading any default
                                configuration files (like .fgfsrc) unless
                                explicitly specified with --config
   --allow-nasal-read=path      Allow Nasal scripts to read files from
                                directories listed as path (separate multiple
                                paths with a semicolon (Windows) or a colon
                                (UNIX)). By default, for security reasons,
                                Nasal scripts can only read data from certain
                                directories, such as $FG_ROOT, $FG_HOME, etc.
   --read-only[={1|0}]          Enable/Disable $FG_HOME read-only
   --ignore-autosave[={1|0}]    Enable/Disable ignoring the autosave file, i.e.
                                the settings saved in this file will not be
                                loaded during startup, nor will the settings be
                                saved to this file when closing the simulator
   --units-feet                 Use feet for distances
   --units-meters               Use meters for distances
   --json-report[={1|0}]        Enable/Disable printing a report in JSON format
                                on the standard output, giving information such
                                as the FlightGear version, $FG_ROOT, $FG_HOME,
                                aircraft and scenery paths, etc.
   --gui[={1|0}]                Enable/Disable GUI (disabling GUI enables
                                headless mode)

   --jsbsim-output-directive-file=file
                                Log JSBSim properties in a CSV file. An output
                                directives file contains an <output
                                type="CSV"></output> element, within which
                                should be specified the parameters or parameter
                                groups that should be logged.

Features:
   --composite-viewer[={1|0}]   Enable/Disable CompositeViewer (extra view
                                windows)
   --panel[={1|0}]              Enable/Disable instrument panel
   --hud[={1|0}]                Enable/Disable Heads Up Display (HUD)
   --anti-alias-hud[={1|0}]     Enable/Disable anti-aliased HUD
   --hud-3d[={1|0}]             Enable/Disable 3D HUD
   --hud-tris                   Hud displays number of triangles rendered
   --hud-culled                 Hud displays percentage of triangles culled
   --random-objects[={1|0}]     Enable/Disable random scenery objects
                                (buildings, etc.)
   --random-vegetation[={1|0}]  Enable/Disable random vegetation objects
   --random-buildings[={1|0}]   Enable/Disable random buildings objects
   --ai-models[={1|0}]          Enable/Disable AI subsystem (required for
                                multi-player, AI traffic and many other
                                animations.) Disabling it is deprecated.
   --ai-traffic[={1|0}]         Enable/Disable artificial traffic.
   --ai-scenario=scenario       Add and enable a new scenario. Multiple options
                                are allowed.
   --freeze[={1|0}]             Enable/Disable start in a frozen state
   --fuel-freeze[={1|0}]        Enable/Disable fuel consumption freeze
   --clock-freeze[={1|0}]       Enable/Disable clock freeze
   --vr[={1|0}]                 Enable/Disable virtual reality
   --restart-launcher[={1|0}]   Enable/Disable automatic opening of the
                                Launcher when exiting FlightGear

Audio Options:
   --show-sound-devices         Show a list of available audio device
   --sound-device               Explicitly specify the audio device to use
   --sound[={1|0}]              Enable/Disable sound effects

Rendering Options:

   --graphics-preset={minimal-quality|low-quality|medium-quality|high-quality|
        ultra-quality}
                                Set graphic options from one of the presets
   --compositor=path            Specify the path to XML file for multi-pass
                                rendering. The path is relative to $FG_ROOT
                                (defaults to Compositor/default.xml).
   --splash-screen[={1|0}]      Enable/Disable splash screen
   --mouse-pointer[={1|0}]      Enable/Disable extra mouse pointer
                                (i.e. for full screen Voodoo based cards)
   --max-fps=Hz                 Maximum frame rate in Hz.
   --bpp=depth                  Specify the bits per pixel
   --fog-disable                Disable fog/haze
   --fog-fastest                Enable fastest fog/haze
   --fog-nicest                 Enable nicest fog/haze

   --distance-attenuation[={1|0}]
                                Enable/Disable runway light distance
                                attenuation
   --horizon-effect[={1|0}]     Enable/Disable celestial body growth illusion
                                near the horizon

   --specular-highlight[={1|0}]
                                Enable/Disable specular reflections on textured
                                objects
   --fov=degrees                Specify field of view angle

   --aspect-ratio-multiplier=factor
                                Specify a multiplier for the aspect ratio.
   --fullscreen[={1|0}]         Enable/Disable fullscreen mode
   --shading-flat               Enable flat shading
   --shading-smooth             Enable smooth shading
   --materials-file=file        Specify the materials file used to render the
                                scenery (default:
                                Materials/regions/materials.xml)
   --texture-filtering=value    Anisotropic Texture Filtering: values should be
                                1 (default), 2, 4, 8 or 16
   --wireframe[={1|0}]          Enable/Disable wireframe drawing mode
   --geometry=WxH               Specify window geometry (640x480, etc)
   --view-offset=value          Specify the default forward view direction as
                                an offset from straight ahead. Allowable values
                                are LEFT, RIGHT, CENTER, or a specific number
                                in degrees
   --texture-cache[={1|0}]      Enable/Disable texture cache (DDS)
   --texture-cache-dir=path     Specify the DDS texture cache directory to be
                                different than the default location

   --terrain-engine={tilecache|pagedLOD}
                                Specify the terrain engine you want to use:
                                tilecache or pagedLOD
   --lod-levels=levels          Specify the detail levels, where levels are a
                                space-separated numeric list of levels. The
                                default is "1 3 5 7 9".
                                Use with --terrain-engine=pagedLOD
   --lod-res=resolution         Specify the resolution of the terrain grid.
                                Defaults is 1.
                                Use with --terrain-engine=pagedLOD

   --lod-texturing={bluemarble|raster|debug}
                                Specify the method of texturing the terrain.
                                The default is bluemarble.
                                Use with --terrain-engine=pagedLOD
   --lod-range-mult=multiplier  Specify the range multiplier (point from low to
                                fine detail). Defaults is 2.
                                Use with --terrain-engine=pagedLOD

Aircraft:
   --aircraft=name              Select an aircraft profile as defined by a top
                                level <name>-set.xml
   --vehicle=name               Same as the --aircraft option
   --aircraft-dir=path          Specify the exact directory to use for the
                                aircraft (normally not required, but may be
                                useful). Interpreted relatively to the current
                                directory. Causes the <path-cache> from
                                autosave_X_Y.xml, as well as --fg-aircraft and
                                the FG_AIRCRAFT environment variable to be
                                bypassed.
   --show-aircraft              Print a list of the currently available
                                aircraft types

   --min-status={alpha|beta|early-production|production}
                                Allows you to define a minimum status level
                                (=development status) for all listed aircraft
   --fdm=name                   Select the core flight dynamics model
                                Can be one of jsb, larcsim, yasim, magic,
                                balloon, ada, external, or null
   --aero=name                  Select aircraft aerodynamics model to load
   --model-hz=n                 Run the FDM this rate (iterations per second)
   --speed=n                    Run the FDM 'n' times faster than real time
   --trim[={1|0}]               Enable/Disable trim the model
                                (only with --fdm=jsbsim)
   --notrim[={1|0}]             Enable/Disable not attempting to trim the model
                                (only with --fdm=jsbsim)
   --on-ground[={1|0}]          Enable/Disable starting at ground level
                                (default enabled)
   --in-air[={1|0}]             Enable/Disable starting in air (implied when
                                using --altitude)
   --auto-coordination[={1|0}]  Enable/Disable auto coordination
   --livery=name                Select aircraft livery
   --state=value                Specify the initial state of the aircraft to
                                the given value

Time Options:

   --timeofday={real|dawn|morning|noon|afternoon|dusk|evening|midnight}
                                Specify a time of day
   --time-offset=[+-]hh:mm:ss   Add this time offset
   --time-match-real            Synchronize time with real-world time
   --time-match-local           Synchronize time with local real-world time

   --start-date-sys=yyyy:mm:dd:hh:mm:ss
                                Specify a starting date/time with respect to
                                system time

   --start-date-gmt=yyyy:mm:dd:hh:mm:ss
                                Specify a starting date/time with respect to
                                GMT

   --start-date-lat=yyyy:mm:dd:hh:mm:ss
                                Specify a starting date/time with respect to
                                local aircraft time

Initial Position and Orientation:
   --airport=ID                 Specify starting position relative to an
                                airport
   --parking-id=name            Specify parking position at an airport (must
                                also specify an airport)
   --parkpos=name               Same as the --parking-id option
   --runway=rwy_no              Specify starting runway (must also specify an
                                airport)
   --carrier={name|ID}          Specify starting position on an AI carrier

   --carrier-position={abeam|FLOLS|name}
                                Specify a starting position relative to the
                                carrier where you can use the predefined abeam
                                (start on downwind abeam) or FLOLS (start on
                                final approach) values, or specify the name of
                                the carrier's parking position. Must also
                                specify a carrier.
   --vor=ID                     Specify starting position relative to a VOR
   --vor-frequency=frequency    Specify the frequency of the VOR. Use with
                                --vor=ID
   --ndb=ID                     Specify starting position relative to an NDB
   --ndb-frequency=frequency    Specify the frequency of the NDB. Use with
                                --ndb=ID
   --fix=ID                     Specify starting position relative to a fix
   --offset-distance=nm         Specify distance to reference point (nautical
                                miles)
   --offset-azimuth=degrees     Specify heading to reference point
   --lon=degrees                Starting longitude (west = -)
   --lat=degrees                Starting latitude (south = -)
   --altitude=value             Starting altitude
   --heading=degrees            Specify heading (yaw) angle (Psi)
   --roll=degrees               Specify roll angle (Phi)
   --pitch=degrees              Specify pitch angle (Theta)
   --uBody=units_per_sec        Specify velocity along the body X axis
   --vBody=units_per_sec        Specify velocity along the body Y axis
   --wBody=units_per_sec        Specify velocity along the body Z axis
   --vNorth=units_per_sec       Specify velocity along a South-North axis
   --vEast=units_per_sec        Specify velocity along a West-East axis
   --vDown=units_per_sec        Specify velocity along a vertical axis
   --vc=knots                   Specify initial airspeed
   --mach=num                   Specify initial mach number
   --glideslope=degrees         Specify flight path angle (can be positive)
   --roc=fpm                    Specify initial climb rate (can be negative)
   --hold-short[={1|0}]         Enable/Disable the move to hold short position
                                for multiplayer

Route/Way Point Options:
   --wp=ID[@alt]                Specify a waypoint for the GC autopilot;
                                multiple instances can be used
   --flight-plan=file           Read all waypoints from a file

Avionics Options:
   --com1=frequency             Set the COM1 radio frequency
   --com2=frequency             Set the COM2 radio frequency
   --nav1=[radial:]frequency    Set the NAV1 radio frequency, optionally
                                preceded by a radial.
   --nav2=[radial:]frequency    Set the NAV2 radio frequency, optionally
                                preceded by a radial.
   --adf1=[rotation:]frequency  Set the ADF1 radio frequency, optionally
                                preceded by a card rotation.
   --adf2=[rotation:]frequency  Set the ADF2 radio frequency, optionally
                                preceded by a card rotation.
   --dme={nav1|nav2|frequency}  Slave the DME to one of the NAV radios, or set
                                its internal frequency.

Environment Options:
   --metar=METAR                Pass a METAR string to set up static weather
                                (this implies --disable-real-weather-fetch)

   --real-weather-fetch[={1|0}]
                                Enable/Disable METAR based real weather
                                fetching
   --clouds[={1|0}]             Enable/Disable 2D (flat) cloud layers
   --clouds3d[={1|0}]           Enable/Disable 3D (volumetric) cloud layers
   --visibility=meters          Specify initial visibility in meters
   --visibility-miles=miles     Specify initial visibility in statute miles

   --wind=DIR[:MAXDIR]@SPEED[:GUST]
                                Specify wind coming from DIR (degrees) at SPEED
                                (knots)
   --random-wind                Set up random wind direction and speed
   --turbulence=0.0 to 1.0      Specify turbulence from 0.0 (calm) to 1.0
                                (severe)

   --ceiling=FT_ASL[:THICKNESS_FT]
                                Create an overcast ceiling, optionally with a
                                specific thickness (defaults to 2000 ft).

Network Options:
   --callsign=name              Assign a unique name to a player

   --multiplay={in|out},hz,address,port
                                Specify multipilot communication settings;
                                multiple instances can be used

   --proxy=[user:pwd@]host:port
                                Specify which proxy server (and port) to use.
                                The username and password are optional and
                                should be MD5 encoded already. This option is
                                only useful when used in conjunction with the
                                real-weather-fetch option.
   --httpd=port                 Enable http server on the specified address.
                                Specify the port or address:port to bind to.
   --telnet=port                Enable telnet server on the specified port
   --jpg-httpd=port             Enable screen shot http server on the specified
                                port (replaced by --httpd)
   --terrasync[={1|0}]          Enable/Disable automatic scenery
                                downloads/updates
   --terrasync-dir=path         Set target directory for scenery downloads
   --fgcom[={1|0}]              Enable/Disable FGCom built-in

   --allow-nasal-from-sockets[={1|0}]
                                Enable/Disable security flag. Enable means that
                                network connections will be allowed full access
                                to the simulator including running arbitrary
                                scripts. Ensure you have adequate security
                                (such as a firewall which blocks external
                                connections).
   --sentry[={1|0}]             Enable/Disable crash and error reports from
                                being sent to the development team for analysis

IO Options:
   --generic=params             Open connection using a predefined
                                communication interface and a preselected
                                communication protocol
   --atlas=params               Open connection using the Atlas protocol
   --atcsim=params              Open connection using the ATC sim protocol
                                (atc610x)
   --AV400=params               Emit the Garmin AV400 protocol required to
                                drive a Garmin 196/296 series GPS
   --AV400Sim=params            Emit the set of AV400 strings required to drive
                                a Garmin 400-series GPS from FlightGear
   --AV400WSimA=params          Open connection for "A" channel using Garmin
                                WAAS GPS protocol
   --AV400WSimB=params          Open connection for "B" channel using Garmin
                                WAAS GPS protocol
   --flarm=params               Open connection using the Flarm protocol, which
                                includes NMEA/GPS and traffic reporting
                                messages
   --garmin=params              Open connection using the Garmin GPS protocol
   --igc=params                 Open connection using the International Gliding
                                Commission protocol
   --joyclient=params           Open connection to an Agwagon joystick
   --jsclient=params            Open connection to a remote joystick
   --native-ctrls=params        Open connection using the FG Native Controls
                                protocol
   --native-gui=params          Open connection using the FG Native GUI
                                protocol
   --native-fdm=params          Open connection using the FG Native FDM
                                protocol
   --native=params              Open connection using the FG Native protocol
   --nmea=params                Open connection using the NMEA protocol
   --opengc=params              Open connection using the OpenGC protocol
   --props=params               Open connection using the interactive property
                                manager
   --pve=params                 Open connection using the PVE protocol
   --ray=params                 Open connection using the Ray Woodworth motion
                                chair protocol
   --rul=params                 Open connection using the RUL protocol

Situation Options:

   --failure={electrical|pitot|static|vacuum}
                                Fail the pitot, static, vacuum, or electrical
                                system (repeat the option for multiple system
                                failures).

Debugging Options:
   --console[={1|0}]            Enable/Disable displaying console (Windows
                                specific)
   --developer[={1|0}]          Enable/Disable developer mode
   --fpe[={1|0}]                Enable/Disable aborting on encountering a
                                floating point exception
   --fgviewer                   Use a model viewer rather than load the entire
                                simulator

   --log-level={bulk|debug|info|warn|alert}
                                Specify which logging level to use

   --log-class={none|ai|aircraft|astro|atc|autopilot|clipper|cockpit|
        environment|event|flight|general|gl|gui|headless|input|instrumentation|
        io|math|nasal|navaid|network|osg|particles|sound|systems|terrain|
        terrasync|undefined|view|all}
                                Specify which logging class(es) to use
   --log-dir={desktop|DIR}      Log to directory DIR. The special value
                                'desktop' causes logging to the desktop
                                (OS-dependent location). This option may be
                                given several times, using a different value
                                each time. Inside the specified directory, the
                                written log file is named
                                FlightGear_YYYY-MM-DD_<num>.log, where <num>
                                takes the values 0, 1, 2, etc.
   --trace-read=property        Trace the reads for a property;
                                multiple instances can be used
   --trace-write=property       Trace the writes for a property;
                                multiple instances can be used
   --uninstall                  Remove $FG_HOME directory. For Windows, it
                                additionally removes TerraSync, Aircraft and
                                TextureCache directories from download
                                directory.
