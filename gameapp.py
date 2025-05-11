import streamlit as st
from typing import List, Optional

# ------------------ GAME STATE ------------------ #
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "current_game": None,
        "number_guess_min": 1,
        "number_guess_max": 50,
        "number_game_count": 0,
        "word_game_count": 0,
        "session_games": [],
        "word_attempts": 0,
        "target_word": None,
        "possible_words": None,
        "_next": "menu"
    }

# ------------------ GLOBALS ------------------ #
WORD_LIST = ["apple", "chair", "elephant", "guitar", "rocket", "pencil", "pizza", "tiger"]
CLUE_QUESTIONS = {
    "Is it a living thing?": lambda word: word in ["apple", "elephant", "tiger"],
    "Is it an animal?": lambda word: word in ["elephant", "tiger"],
    "Is it an object?": lambda word: word in ["chair", "guitar", "rocket", "pencil", "pizza"],
    "Is it used in school?": lambda word: word in ["chair", "pencil"],
    "Is it a musical instrument?": lambda word: word == "guitar",
    "Is it edible?": lambda word: word in ["apple", "pizza"],
    "Does it have four legs?": lambda word: word in ["elephant", "tiger", "chair"],
    "Can it fly?": lambda word: word == "rocket",
    "Is it made by humans?": lambda word: word in ["chair", "guitar", "rocket", "pencil", "pizza"],
    "Is it made of wood?": lambda word: word in ["chair", "guitar", "pencil"],
    "Does it live in the jungle?": lambda word: word in ["elephant", "tiger"],
    "Is it a type of furniture?": lambda word: word == "chair",
    "Is it a vehicle?": lambda word: word == "rocket",
    "Can it be eaten raw?": lambda word: word == "apple",
    "Does it have strings?": lambda word: word == "guitar",
    "Is it a type of stationery?": lambda word: word == "pencil",
    "Is it round in shape?": lambda word: word == "pizza",
    "Is it bigger than a person?": lambda word: word in ["elephant", "rocket"],
    "Is it commonly found in a classroom?": lambda word: word in ["chair", "pencil"]
}

state = st.session_state.game_state
st.title("🕹️ Multi-Game Bot")

# ------------------ MAIN MENU ------------------ #
if state["_next"] == "menu":
    st.header("Main Menu")
    st.write(f"Number Games Played: {state['number_game_count']}")
    st.write(f"Word Games Played: {state['word_game_count']}")
    choice = st.radio("Choose a game:", ["Number Game", "Word Game", "Exit"])

    if st.button("Start Game"):
        if choice == "Number Game":
            state["current_game"] = "number"
            state["_next"] = "start_number_game"
        elif choice == "Word Game":
            state["current_game"] = "word"
            state["_next"] = "start_word_game"
        else:
            st.write("👋 Goodbye!")
            st.stop()
    st.stop()

# ------------------ NUMBER GUESSING GAME ------------------ #
elif state["_next"] == "start_number_game":
    min_val = state["number_guess_min"]
    max_val = state["number_guess_max"]
    mid = (min_val + max_val) // 2

    st.subheader("🤖 Number Guessing Game")
    st.write(f"Is your number greater than **{mid}**?")
    col1, col2 = st.columns(2)
    if col1.button("Yes"):
        state["number_guess_min"] = mid + 1
        state["_next"] = "start_number_game"
        st.rerun()
    if col2.button("No"):
        state["number_guess_max"] = mid
        state["_next"] = "start_number_game"
        st.rerun()

    if state["number_guess_min"] == state["number_guess_max"]:
        st.success(f"🎉 Your number is **{state['number_guess_min']}**! I guessed it!")
        state["number_game_count"] += 1
        state["session_games"].append("number")
        state["number_guess_min"] = 1
        state["number_guess_max"] = 50
        state["_next"] = "menu"
        if st.button("Back to Menu"):
            st.rerun()
    st.stop()

# ------------------ WORD GUESSING GAME ------------------ #
elif state["_next"] == "start_word_game":
    st.subheader("🧠 Word Guessing Game")

    if state["possible_words"] is None:
        state["possible_words"] = WORD_LIST.copy()

    if state["target_word"] is None:
        st.write("Think of a word from this list:")
        st.info(", ".join(WORD_LIST))
        target = st.text_input("Enter your secret word (for testing only):")
        if target:
            state["target_word"] = target.strip().lower()
            st.rerun()
        st.stop()

    if state["word_attempts"] < 5 and state["word_attempts"] < len(CLUE_QUESTIONS):
        questions = list(CLUE_QUESTIONS.keys())
        question_idx = state["word_attempts"]
        question = questions[question_idx]

        st.write(f"Question {question_idx + 1}: {question}")
        answer = st.radio("Your answer:", ["Yes", "No", "Maybe"])

        if st.button("Submit Answer"):
            predicate = CLUE_QUESTIONS[question]
            filtered = []

            for word in state["possible_words"]:
                try:
                    if answer == "Yes" and predicate(word):
                        filtered.append(word)
                    elif answer == "No" and not predicate(word):
                        filtered.append(word)
                    elif answer == "Maybe":
                        filtered.append(word)
                except Exception:
                    continue

            state["possible_words"] = filtered
            state["word_attempts"] += 1

            if len(filtered) == 1:
                guess = filtered[0]
                st.success(f"I think your word is: **{guess}**")
                correct = st.radio("Am I right?", ["Yes", "No"])
                if st.button("Submit Confirmation"):
                    if correct == "Yes":
                        st.balloons()
                        st.success("🎉 Yay! I guessed your word!")
                        state["word_game_count"] += 1
                        state["session_games"].append("word")
                        state["possible_words"] = None
                        state["word_attempts"] = 0
                        state["target_word"] = None
                        state["_next"] = "menu"
                        st.rerun()
                    else:
                        st.warning("Hmm, let me try again.")
                        state["possible_words"] = WORD_LIST.copy()
                        state["word_attempts"] = 0
                        state["target_word"] = None
                        st.rerun()
            elif len(filtered) == 0:
                st.error("😕 No matching words found. Maybe one of the answers was off?")
                retry = st.radio("Would you like to retry?", ["Yes", "No"])
                if st.button("Submit Choice"):
                    if retry == "Yes":
                        state["possible_words"] = WORD_LIST.copy()
                        state["word_attempts"] = 0
                        state["target_word"] = None
                        st.rerun()
                    else:
                        state["word_game_count"] += 1
                        state["session_games"].append("word")
                        state["possible_words"] = None
                        state["word_attempts"] = 0
                        state["target_word"] = None
                        state["_next"] = "menu"
                        st.rerun()
            else:
                st.info(f"🔎 Remaining possible words: {', '.join(filtered)}")
                st.rerun()
        st.stop()
    else:
        # Final guess attempt
        if state["possible_words"]:
            guess = state["possible_words"][0]
            st.warning(f"My final guess is: **{guess}**")
            correct = st.radio("Am I right?", ["Yes", "No"])
            if st.button("Submit Final Answer"):
                if correct == "Yes":
                    st.balloons()
                    st.success("🎉 Yay! I guessed your word!")
                else:
                    st.error(f"Oops! The correct word was: **{state['target_word']}**")
                state["word_game_count"] += 1
                state["session_games"].append("word")
                state["possible_words"] = None
                state["word_attempts"] = 0
                state["target_word"] = None
                state["_next"] = "menu"
                st.rerun()
        else:
            st.error("No possible words left to guess.")
            state["word_game_count"] += 1
            state["session_games"].append("word")
            state["possible_words"] = None
            state["word_attempts"] = 0
            state["target_word"] = None
            state["_next"] = "menu"
            if st.button("Back to Menu"):
                st.rerun()
    st.stop()
