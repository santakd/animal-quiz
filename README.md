### 🐾 Animal Quiz Show

This has two versions of the animal quiz.
- A lightweight, fully responsive, zero-dependency trivia game built with pure HTML5, CSS3, and Vanilla JavaScript.
- A Python, PyGame and SQLite version of the quiz

**No servers. No build steps. Just open and play!** 🎉

Designed with simplicity in mind, this project allows anyone to quickly set up an educational and interactive quiz. 

It dynamically selects random animals, generates multiple-choice questions, and calculates your score—all straight from your local favorite web browser.

![animal-quiz.gif](https://github.com/santakd/animal-quiz/blob/main/animal-quiz.gif)

 
---

### ✨ Features

* 🚫 **100% Serverless:** Runs locally using the `file://` protocol. No Node.js, or Apache servers required!
* 🐍 **Python Version:** Runs after setting up the SQLite DB and then running the quiz program.
* 📱 **Fully Responsive:** Beautiful, modern UI powered by CSS Grid and Flexbox. Looks great on desktop monitors and mobile phones alike.
* 🔀 **Smart Randomization:** Utilizes the **Fisher-Yates Shuffle algorithm** to ensure questions and multiple-choice answers are completely randomized every time you play.
* ⚙️ **Dynamic Scaling:** Want 10 questions? 20? 50? Just change one variable (`QUESTIONS_PER_GAME`). The game's UI and math will automatically adapt.
* 🛡️ **Fail-Safe Logic:** If you request 20 questions but only have 15 animals configured, the game intelligently scales itself down to 15 to prevent crashing.
* 🎨 **Instant Visual Feedback:** Smooth CSS animations and color-coded feedback (Green for correct, Red for incorrect with the correct answer highlighted).


---

### 🚀 How to Run

##### For the web version. because this app doesn't require a server, installation takes less than a minute.

1. **Download or Clone** this repository to your local machine.
2. **Create your image directory:** Inside the project folder, ensure there is a folder named `img`.
3. **Add your images:** Place your animal GIF files inside the `img` folder. 
   * *Important:* Files must be named in the format: `<Animal Name> 512.gif` (e.g., `Lion 512.gif`, `Red Panda 512.gif`).
4. **Edit:** `index_max.html` and then minify it to `index_min.html`
5. **Play:** Double-click `index_min.html` to open it in Chrome, Safari, Firefox, or Edge.

##### For the python version, it needs Python 3.x, PyGame, Pillow and SQLite
1. **Install the pre-requisites:** Pip install PyGame Pillow
2. **Database:** SQLite3 is pre-installed on Mac
3. **To setup the DB:** Run Python3 setup_db.py
4. **To play the quiz:** Run Python3 animal_quiz.py

---

### 🛠️ Customization & Configuration

You can easily modify the game by opening `index_max.html` in any text editor and tweaking the **Configuration** section near the top of the `<script>` block.
Remember to minify `index_max.html` to `index_min.html`

#### 1. Changing the Number of Questions
Want a shorter or longer game? Change this single constant. The UI, progress trackers, and final score calculations will automatically update!
```javascript
const QUESTIONS_PER_GAME = 20; 
```

#### 2. Adding Custom Animals
Modern web browsers have strict security rules that prevent local JavaScript from reading your hard drive to see what files are in your `img` folder. 
Therefore, you must tell the script what animals are available.

Simply add the exact names of your animals to the `animalNames` array. 
**Do not include the " 512.gif" part in the array**

Refer the `array_gen.py` utility to generate the array from the files in img folder

```javascript
const animalNames = [
    "Dog", "Cat", "Elephant", "Lion", "Tiger", 
    "My Custom Animal", "Another Animal" // <-- Add yours here!
];
```

#### 3. Using Different Image Formats
Prefer `.jpg` or `.png` over `.gif`? Or maybe you don't want the " 512" in the filename? Just modify the `FILE_SUFFIX` constant:
```javascript
// Change this to match your file naming convention
const FILE_SUFFIX = ".jpg"; 
```

---

### 🧠 Under the Hood

For Web Version
* **HTML5:** Semantic structure for accessibility.
* **CSS3:** Uses native CSS variables (`:root`) for easy theming. You can change the primary colors globally in seconds.
* **Vanilla JavaScript (ES6+):** Utilizes array mapping, filtering, arrow functions, and DOM manipulation without the bloat of external libraries like React or jQuery.

For Python Version
* **Python 3**
* **Dependencies:** PyGame, Pillow and SQLite 

---

### 💻 Developer Notes

##### For the web version
The HTML file implements a simple, interactive animal quiz game using vanilla JavaScript, CSS, and HTML. 
It displays a series of animal images (stored in an img/ folder) and asks users to select the correct name from four multiple-choice options. 
The game adapts dynamically to the number of available animals and questions configured, providing feedback and a final score. 
At a high level, it follows web development principles like separation of concerns (HTML for structure, CSS for styling, JS for behavior), 
responsive design for mobile compatibility, and event-driven programming to handle user interactions.

```
/ (Root)
├── index_min.html    # Minified index html file
├── index_max.html    # Standard index html file
├── minifybs4.py      # Minification utility using BeautifulSoup, required only for minifying the index_max.html, not required at runtime 
├── minifystd.py      # Minification utility using Standard libray, required only for minifying the index_max.html, not required at runtime
├── array_gen.py      # Python utility to generate the javascript encrypted array based on img folder contents, not required at runtime
├── array_enc.txt     # Output of the array_gen.py which has the javascript encrypted array and can be copied to index_max.html, not required at runtime
├── array_txt.txt     # Output of the array_gen.py which has the javascript unencrypted array for debugging if required, not required at runtime
├── /img/             # Source directory for "<Animal> 512.gif" files (User populated, required at runtime for the web version)
└── /logs/            # Stores timestamped .log files produced by the python utilities
```

The HTML structure defines three main screens: a start screen with an introduction and start button, a quiz screen showing the current question with
an image and choice buttons, and a results screen displaying the score and feedback. Elements are organized in a centered container with IDs for easy
JavaScript access. The <script> tag contains all the game logic, making it self-contained without external dependencies. This approach keeps the code 
modular but could be improved by separating JS into its own file for better maintainability in larger projects.

The CSS uses CSS custom properties (variables) for colors and fonts, enabling easy theming changes. It employs Flexbox and Grid for layout, 
ensuring the quiz container is centered and responsive. Animations like fadeIn add polish, while media queries adjust the grid for smaller screens.
Key styling principles include accessibility (e.g., hover states and disabled button handling) and visual hierarchy (e.g., larger fonts for headings).
A potential gotcha is the use of !important in button classes, which overrides specificity but can lead to cascading issues if styles expand.

The JavaScript code is divided into sections for clarity: configuration (constants for questions, file paths, and animal names), 
application state (variables tracking progress), DOM references (cached elements for efficiency), utility functions (shuffle algorithm and screen switching),
and quiz logic (initialization, question generation, and answer handling). It initializes on page load, shuffles animals to randomize questions, and uses event
listeners for button clicks. The Fisher-Yates shuffle ensures fair randomization, a common algorithm for unbiased permutations. 
Event handling disables buttons after selection to prevent multiple answers, with a timeout for feedback before advancing.

Question generation creates an array of objects, each with a correct answer, shuffled choices, and an image path.
This data-driven approach makes the code flexible—changing QUESTIONS_PER_GAME or the animalNames array automatically updates the UI. 
Answer validation provides immediate visual feedback (green for correct, red for incorrect) and highlights the right choice if wrong. 
The end-game logic calculates a percentage-based message, promoting engagement. A subtle gotcha is the reliance on exact filename matches; 
mismatches could cause broken images, as handled by the onerror attribute. For improvements, consider adding error handling for missing images or 
using a framework like React for state management in more complex apps. Overall, this code demonstrates fundamental web concepts like DOM manipulation, 
asynchronous delays with setTimeout, and conditional rendering via CSS classes, making it a great starting point for beginners learning interactive web development.

##### For the python version

This project is a desktop port of a web-based quiz game. It consists of a database ingestion utility (setup_db.py) and a Pygame-based main client (animal_quiz.py). The system is entirely offline, using SQLite for data/asset storage and Pillow (PIL) to overcome Pygame's native limitations with animated GIFs.
Directory Architecture

The application strictly enforces the following structure. The scripts will auto-generate the db and logs directories if they do not exist.

```
/ (Root)
├── setup_db.py       # DB initialization & asset ingestion script
├── animal_quiz.py    # Main Pygame application
├── /img/             # Source directory for "<Animal> 512.gif" files (User populated, not required after setup for the python version)
├── /db/              # Stores animal_quiz.sqlite which is created after running setup_db.py
└── /logs/            # Stores timestamped .log files
```

**Component: setup_db.py**

This script serves as the Database Architect and Data Pipeline.

```
Idempotency: The script drops and recreates tables (app_users and animals) on execution. It is safe to run multiple times without corrupting the database.

Security: SQLite lacks native database-level passwords. Authentication is handled via an application-level app_users table. The default password is stored as a SHA-256 hash using Python's hashlib.

BLOB Ingestion: Scans the /img folder, strips the " 512.gif" suffix to derive the animal's name, converts the file into binary data, and stores it in the image_blob column.
```

**Component: animal_quiz.py**

This is the main Pygame client. It operates on a continuous, non-blocking event loop governed by a State Machine.
```
    State Machine: LOGIN -> START -> QUIZ -> DELAY -> RESULT -> START.

    Bespoke UI Elements: Because Pygame has no built-in UI library, the TextInput and Button classes were built from scratch to handle hover states, mouse events, masking (for passwords), and active/disabled states.

    The Animated GIF Workaround (Crucial): Pygame's image.load() only reads the first frame of a GIF. To solve this, the AnimatedGIF class:

        Reads the BLOB data from SQLite into memory using io.BytesIO.

        Uses Pillow (PIL.ImageSequence) to extract every individual frame and its duration.

        Converts each frame into a pygame.Surface.

        Manages a custom timer in the update_logic() loop to cycle through frames at the correct speed.

    Layout Adjustments: The screen is intentionally sized to 800x850 to comfortably fit the large 512x512 pixel GIFs without overlapping the answer buttons below them.

    Font Limitations: Emojis were removed from the Result Screen feedback messages because Pygame's default SysFont renderer crashes or renders empty squares when attempting to draw colored Unicode emojis.
```

**Setup & Execution Instructions**

Prerequisites: Python 3.9+ installed.

```
1. Install dependencies
pip install pygame Pillow

2. Add your GIF files to the /img directory (e.g., /img/Lion 512.gif)

3. Initialize the database and ingest images
python setup_db.py

4. Run the game (Default Login - User: admin | Pass: password123)
python animal_quiz.py

5. Troubleshooting / Logging

Both scripts utilize Python's logging module.

    Logs are pushed to stdout (the console) and simultaneously saved to /logs/ with a timestamp.

    If a Pygame crash occurs, or if an image fails to parse from the BLOB, check the latest log file for the stack trace. The AnimatedGIF class is wrapped in a try/except block to prevent corrupted BLOBs from crashing the main game loop.
```
    
---

### 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
Feel free to check [issues page](https://github.com/your-username/your-repo-name/issues) if you want to contribute.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


---

### 📝 License

Distributed under the MIT License. See `LICENSE` for more information.


---

*If you like this project, please consider giving it a ⭐ on GitHub!*
 
