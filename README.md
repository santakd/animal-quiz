### 🐾 Animal Quiz Show

A lightweight, fully responsive, zero-dependency trivia game built with pure HTML5, CSS3, and Vanilla JavaScript. 

**No servers. No build steps. Just open and play!** 🎉

Designed with simplicity in mind, this project allows anyone to quickly set up an educational and interactive quiz. 

It dynamically selects random animals, generates multiple-choice questions, and calculates your score—all straight from your local favorite web browser.

![animal-quiz.gif](https://github.com/santakd/animal-quiz/blob/main/animal-quiz.gif)

 
---

### ✨ Features

* 🚫 **100% Serverless:** Runs locally using the `file://` protocol. No Node.js, Python, or Apache servers required!
* 📱 **Fully Responsive:** Beautiful, modern UI powered by CSS Grid and Flexbox. Looks great on desktop monitors and mobile phones alike.
* 🔀 **Smart Randomization:** Utilizes the **Fisher-Yates Shuffle algorithm** to ensure questions and multiple-choice answers are completely randomized every time you play.
* ⚙️ **Dynamic Scaling:** Want 10 questions? 20? 50? Just change one variable (`QUESTIONS_PER_GAME`). The game's UI and math will automatically adapt.
* 🛡️ **Fail-Safe Logic:** If you request 20 questions but only have 15 animals configured, the game intelligently scales itself down to 15 to prevent crashing.
* 🎨 **Instant Visual Feedback:** Smooth CSS animations and color-coded feedback (Green for correct, Red for incorrect with the correct answer highlighted).


---

### 🚀 How to Run

Because this app doesn't require a server, installation takes less than a minute.

1. **Download or Clone** this repository to your local machine.
2. **Create your image directory:** Inside the project folder, ensure there is a folder named `img`.
3. **Add your images:** Place your animal GIF files inside the `img` folder. 
   * *Important:* Files must be named in the format: `<Animal Name> 512.gif` (e.g., `Lion 512.gif`, `Red Panda 512.gif`).
4. **Play:** Double-click `index.html` to open it in Chrome, Safari, Firefox, or Edge.


---

### 🛠️ Customization & Configuration

You can easily modify the game by opening `index.html` in any text editor and tweaking the **Configuration** section near the top of the `<script>` block.

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

* **HTML5:** Semantic structure for accessibility.
* **CSS3:** Uses native CSS variables (`:root`) for easy theming. You can change the primary colors globally in seconds.
* **Vanilla JavaScript (ES6+):** Utilizes array mapping, filtering, arrow functions, and DOM manipulation without the bloat of external libraries like React or jQuery.


---

### 💻 Developer Notes

The HTML file implements a simple, interactive animal quiz game using vanilla JavaScript, CSS, and HTML. 
It displays a series of animal images (stored in an img/ folder) and asks users to select the correct name from four multiple-choice options. 
The game adapts dynamically to the number of available animals and questions configured, providing feedback and a final score. 
At a high level, it follows web development principles like separation of concerns (HTML for structure, CSS for styling, JS for behavior), 
responsive design for mobile compatibility, and event-driven programming to handle user interactions.

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
 
