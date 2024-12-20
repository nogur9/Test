import streamlit as st
import openai
import re

# Set your OpenAI API key
openai.api_key = "Your_key"
MODEL_NAME = "gpt-3.5-turbo"
MAX_TOKENS = 150
IMAGE_SIZE = "1024x1024"

st.title("AI Prompt App")
# Input prompt from the user


def create_image(prompt:str):

    # Generate the image
    response = openai.Image.create(
        prompt=prompt,
        n=1,  # Number of images to generate
        size="1024x1024"  # Image size, can be 256x256, 512x512, or 1024x1024
    )

    # Get the URL of the generated image
    image_url = response['data'][0]['url']
    st.write("Generated Image URL:", image_url)



def get_ai_feedback(prompt: str) -> str:
    """Gets feedback from the AI model."""

    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"AI Feedback error: {e}")
        return ""


def test_if_prompt_good_enough(user_prompt, ai_response):
    if ai_response.endswith("Pass"):
        st.session_state.user_prompt = user_prompt
        return True
    else:
        return False


def evaluate_prompt_with_heuristics(prompt):
    """Evaluates the quality of the prompt."""
    if len(prompt.split(" ")) < 3:
        return "The prompt is too short and written like a Google search."
    elif ("cat" not in prompt.lower()) and ("breed" not in prompt):
        return "The prompt isn't containing relevant information."
    elif len(prompt.split(" ")) > 300:
        return "prompt too long"
    else:
        return None


def get_cat_breeds_list(text: str):
    regex = r'cat_breeds = (\[.*?\])'

    extraction_prompt = f"""
        Hey :)
        Please extract as a python list, the names of cat breeds from the next sentence:
        {text}\n\n


        For example,
        if sentence = "The Nebelung is a pedigree breed of domestic cat. Nebelungs have long bodies, wide-set green eyes, long and dense fur, and mild dispositions.[1] The cat is related to the Russian Blue, but with longer, silkier hair, and is in fact sometimes called the Long-haired Russian Blue."
        good output:
        "Here's the extracted list of cat breeds:
        python
        cat_breeds = ['Nebelung', 'Russian Blue', 'Long-haired Russian Blue']
        "
        """

    ai_response = get_ai_feedback(extraction_prompt)
    match = re.search(regex, ai_response)
    if match:
        cat_breeds_list = match.group(1)
        print(cat_breeds_list)
        return cat_breeds_list

def screen_1():
    user_prompt = st.text_area("Enter your prompt:")
    evaluation_prompt = f"""
        Please evaluate the quality of the following prompt for learning about cat breeds, 
        and provide feedback on how to improve it:\n\n"
        Prompt: {user_prompt}\n\n
        Your feedback should include: 
        1. Whether the prompt is too broad, too short, or too specific. 
        2. Suggestions for improving the prompt to get a better response.


        If the user's prompt is sufficient please write "Pass" in the end of your response.
        But, write this "Pass" only if the prompt is good enough.
        If there are big issues with the user's prompt, don't write this "Pass", 
        but, if there are only small issues with it, do write "Pass" in the end of your response



        For example,
        if user_prompt = "Different cat breeds"
        A good response is:
        "The prompt is too similar to google search, please try a different prompt"

        if user_prompt = "Hello, please tell me about World-War II"
        A good response is:
        "The prompt isn't requesting information about cat breeds, please try a different prompt"



        if user_prompt = "Hello, please tell me about some various cat breeds"
        A good response is:
        "The prompt is good \n Pass"
        """

    # Button to generate a response
    if st.button("Generate Response"):
        response = evaluate_prompt_with_heuristics(user_prompt)

        # if heuristics cancelled it
        if response is not None:
            st.write("### Heuristic Response:")
            st.write(response)

        # if the prompt passes heuristics
        else:
            # Call the OpenAI API to get the response

            # Extract and display the AI's response
            ai_response = get_ai_feedback(evaluation_prompt)
            st.write("### AI Response:")
            st.write(ai_response)
            prompt_is_good_enough = test_if_prompt_good_enough(user_prompt, ai_response)
            if prompt_is_good_enough:
                st.session_state.screen_num = 2

                # Extract and display the AI's response
                ai_response = get_ai_feedback(st.session_state.user_prompt)
                st.session_state.ai_response = ai_response
                st.rerun()



def screen_2():
    st.write("### AI Response:")
    st.write(st.session_state.ai_response)

    cat_breed_choices = get_cat_breeds_list(st.session_state.ai_response)

    option = st.selectbox(
        "Select the chosen cat breed:",
        eval(cat_breed_choices))

    if st.button("Next"):
        print(f"{option = }")
        st.session_state.chosen_cat_breed = option
        st.session_state.screen_num = 3
        st.rerun()


def screen3():
    cat_breed = st.session_state.chosen_cat_breed
    suggested_prompt = f"A serene scene of the {cat_breed} standing on a mountain at sunset with a lake in the background."
    st.write(suggested_prompt)
    user_prompt = st.text_area("Enter your prompt:")

    if st.button("Generate image"):
        create_image(user_prompt)


if __name__ == "__main__":

    if 'screen_num' not in st.session_state:
        st.session_state.screen_num = 1

    if st.session_state.screen_num == 1:
        screen_1()

    elif st.session_state.screen_num == 2:
        screen_2()

    elif st.session_state.screen_num == 3:
        screen3()

    else:
        raise ValueError("unknown screen number")


