import streamlit as st

from reverso_connection import ReversoConnection

# Use st.experimental_connection to create the connection
main_conn = st.experimental_connection("reverso", type=ReversoConnection)

# Get the supported languages from the connection
supported_langs = main_conn.get_supported_langs()


# Streamlit app
def main():
    # Title of the app
    st.markdown(
        "<h1 style='text-align: center; color: blue;'>Reverso API Connection</h1>",
        unsafe_allow_html=True,
    )

    # Use st.form to create the form
    with st.form("ReversoForm"):
        st.write("Enter the source and target languages and the text to be translated:")

        # Source language selection
        source_lang = st.selectbox(
            "Source Language", ["en"] + list(supported_langs["source_lang"])
        )

        # Target language selection
        target_lang = st.selectbox(
            "Target Language", ["fr"] + list(supported_langs["target_lang"])
        )

        # Number of usage examples
        n_ex = st.slider("Select the number of examples you want to see", 5, 50, 10)

        # Examples list
        examples = [
            "Hello, how are you?",
            "The sun is shining.",
            "I want to go on vacation.",
            "Life is beautiful.",
        ]
        example = st.radio("Choose an example...", examples, key="chosen_example")

        # User input for the text to translate
        user_input = st.text_input("...or enter a text", example)

        # Submit button
        submitted = st.form_submit_button("Translate & Get Examples!")

    # Process form submission
    if submitted:
        # Use st.experimental_connection to create the connection
        connection = st.experimental_connection(
            "reverso",
            type=ReversoConnection,
            source_text=user_input,
            source_lang=source_lang,
            target_lang=target_lang,
        )

        # Clear cache if any
        st.cache_data.clear()

        st.session_state.is_connection = True

        # Get translations and usage examples
        translations = connection.get_usage_translations()
        usage_examples = connection.get_usage_examples(n_ex=n_ex)

        # Display translations in one column
        with st.expander("Translations"):
            st.dataframe(translations)

        # Display usage examples in another column
        with st.expander("Usage Examples"):
            st.dataframe(usage_examples)

    # Click on help to see what can do the connection
    with st.expander("Connection help"):
        st.help(main_conn)

    # Click to reset the connection
    _ = st.button("Reset the connection", key="reset")

    if st.session_state.reset and st.session_state.is_connection:
        main_conn.reset()
        st.session_state.is_connection = False


if __name__ == "__main__":
    main()
