#include <windows.h>
#include <string>

int WINAPI WinMain(
    HINSTANCE hInstance,
    HINSTANCE hPrevInstance,
    LPSTR lpCmdLine,
    int nShowCmd
) {
    char path[MAX_PATH] = {0};

    // Get full path of the running executable
    GetModuleFileNameA(NULL, path, MAX_PATH);

    std::string message = "executed from:\n";
    message += path;

    MessageBoxA(
        NULL,
        message.c_str(),
        "Execution Test",
        MB_OK | MB_ICONINFORMATION
    );

    return 0;
}

