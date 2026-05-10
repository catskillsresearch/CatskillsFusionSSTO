


Here is your complete Systems Engineer operations cheat sheet for the Orbitron Test Stand. 

### ⚙️ Reactor Operation (Custom Keybinds)
| Key / Input | Action | What it does in the Simulation |
| :--- | :--- | :--- |
| **`Spacebar`** | **Toggle Ignition** | Arms the reactor, starts the JSBSim 0D physics loop, and triggers the heavy transformer audio. Press again to shut down. |
| **`w`** | **Throttle UP** | Increases the Neutral Beam Injector (NBI) flow rate. Watch the Canvas HUD—Gross Power, Amps, and Heat will climb! |
| **`s`** | **Throttle DOWN** | Decreases the NBI flow rate. |

### 🎥 Camera & Viewpoint Controls
| Key / Input | Action | What it does in the Simulation |
| :--- | :--- | :--- |
| **`Right-Click`** | **Toggle Mouse-Look** | Hides the mouse cursor and turns it into a crosshair. Move your physical mouse to look around freely. Right-click again to get your cursor back. |
| **`v`** | **Cycle Views (Fwd)** | Jumps between different camera angles (Operator View, Helicopter/External View, Chase, Tower). |
| **`Shift + v`** | **Cycle Views (Rev)** | Cycles backwards through the camera angles. |
| **`x`** | **Zoom In** | Magnifies the view. |
| **`Shift + x`** | **Zoom Out** | Pulls the camera back for a wider field of view. |

### 🛠️ Interaction & Debugging Tools
| Key / Input | Action | What it does in the Simulation |
| :--- | :--- | :--- |
| **`Ctrl + c`** | **Highlight Clickables** | Instantly turns any clickable 3D object (like your Operator Console) bright yellow so you don't have to guess where the invisible "hitbox" is. |
| **`Left-Click`** | **Interact** | Clicks the 3D console to trigger the ignition (Alternative to using the Spacebar). |
| **`Alt + F2`** | **Reload 3D Model** | If you ever edit the XML file to move or scale the 3D model, pressing this reloads it instantly without needing to restart FlightGear. |

**Your Startup Sequence:**
1. Launch the sim.
2. The crisp green 2D Holographic HUD will appear on your screen.
3. Press **`Spacebar`** to arm the system.
4. Hold **`w`** to push the NBI throttle to 100 sccm and watch your 3.5 MW Breakeven math calculate in real time!
