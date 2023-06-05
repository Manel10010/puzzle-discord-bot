# Discord Puzzle Bot for ACE Event

Welcome to the repository for the Discord Puzzle Bot designed specifically for the ACE (Curricular Extension Activity)event. This bot serves as an integral part of the event, facilitating interactions between participants and providing an immersive puzzle-solving experience.

The ACE Puzzle Bot is equipped with powerful features that enhance the gameplay. It allows participants to submit their answers to puzzles, providing a seamless and efficient method of response collection. Additionally, the bot assists players by directing them to the locations of the next enigmas, ensuring a smooth progression throughout the event.

One notable aspect of the bot is its ability to administer punishments. It ensures fair play by penalizing players who violate event rules or attempt to gain an unfair advantage. The punishment system is designed to maintain a level playing field, promoting healthy competition and ensuring that participants adhere to the event guidelines.

This repository serves as a centralized hub for the development and maintenance of the ACE Puzzle Bot. Here, you will find the source code, documentation, and resources related to the bot's functionality. Feel free to explore, contribute, and enhance the bot's capabilities as we strive to create a memorable and engaging puzzle-solving experience for ACE participants.

# Explain of each function
**MyClient**
- This especific class extends discord.Client class and represents your custom Discord bot client.
- __init__ method is the constructor for the MyClient class. It initializes the client with the provided intents and creates an instance of the app_commands.CommandTree class stored in the self.tree attribute.
- **setup_hook** is an asynchronous method that sets up the command tree by copying global commands to a specific guild (MY_GUILD) and synchronizing the tree.
- **on_member_join** is an asynchronous method called when a member joins the server. It prints a message with the mention of the new member and retrieves the log channel using the provided channel ID. The code also includes additional functionality related to data handling and sending welcome messages.
- **on_message** is an asynchronous method called when a message is sent. Currently, it is an empty method and doesn't perform any actions. My intention with that method was to try to see if some players would type the answer incorrectly by a small margin, such as typing "Purple" instead of "purple". I wanted to send a message to the user indicating that their answer was correct but they made a minor mistake. However, I later discovered a better solution using the **.upper()** method in Python, which effectively solves the problem.
