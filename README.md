# Universal Asset Browser
A tool for digital creators to unify asset access and management across content creation applications. 

# Installation
- Desktop:
    1. Clone the repo.
    2. Install it to a Python interpreter.
    3. Execute the package.

- Houdini:
    1. Clone the repo.
    2. Install it to a new Python interpreter.
    3. Create a directory named `uab` and a `uab.json` file in `$HOUDINI_USER_PREF_DIR/packages`.
    4. Copy the following to `uab.json`:
        ```json
        {
            "hpath": "$HOUDINI_USER_PREF_DIR/packages/uab"
        }
        ```
    5. Create a directory named `python_panels` and a `uab_interface.pypanel` file in the `uab` directory.
    6. Copy the following to `uab_interface.pypanel`:
        ```xml
        <?xml version="1.0" encoding="UTF-8"?>
        <pythonPanelDocument>
        <!-- This file contains definitions of Python interfaces and the
        interfaces menu.  It should not be hand-edited when it is being
        used by the application.  Note, that two definitions of the
        same interface or of the interfaces menu are not allowed
        in a single file. -->
        <interface name="uab_interface" label="Universal Asset Browser" icon="MISC_python" showNetworkNavigationBar="false" help_url="">
            <script><![CDATA[
        def onCreateInterface():
            import uab.runner
            return uab.runner.run()

        ]]></script>
            <includeInPaneTabMenu menu_position="0" create_separator="true"/>
            <includeInToolbarMenu menu_position="212" create_separator="false"/>
            <help><![CDATA[]]></help>
        </interface>
        </pythonPanelDocument>
        ```
    7. Create a directory named `python3.11libs` and copy the contents of the interpreter's `site_packages` to it.
    8. Create a new pane in Houdini and select the "Universal Asset Browser".
