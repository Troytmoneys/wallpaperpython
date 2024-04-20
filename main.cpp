#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <filesystem>
#include <fstream>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <Windows.h>
#include <shellapi.h>
#include <tchar.h>
#include <shlobj.h>

using namespace std;
using json = nlohmann::json;

const string UNSPLASH_ACCESS_KEY = "ESoVUH1y2o_Ymf0D75dGwQ-5PbTFcVlCxGUezWbVonA";
const string PEXELS_API_KEY = "0C9jOgR1p85iMebGlpr7StHWBDy03pCUJzd1xRkeuKeg9zw0GbalHJ9F";

string temp_folder;
string desired_folder;
string current_wallpaper_path;

HBITMAP create_image() {
    HBITMAP hBitmap;
    HDC hdc = GetDC(NULL);
    hBitmap = CreateCompatibleBitmap(hdc, 64, 64);
    HDC memdc = CreateCompatibleDC(hdc);
    SelectObject(memdc, hBitmap);
    HBRUSH hBrush = CreateSolidBrush(RGB(255, 0, 0));
    FillRect(memdc, &RECT{0, 0, 64, 64}, hBrush);
    DeleteObject(hBrush);
    hBrush = CreateSolidBrush(RGB(0, 255, 0));
    FillRect(memdc, &RECT{16, 16, 48, 48}, hBrush);
    DeleteObject(hBrush);
    DeleteDC(memdc);
    ReleaseDC(NULL, hdc);
    return hBitmap;
}

string fetch_wallpaper() {
    vector<string> sources = {"unsplash", "bing", "pexels"};
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> dis(0, sources.size() - 1);
    string source = sources[dis(gen)];

    string image_url;
    if (source == "unsplash") {
        CURL* curl = curl_easy_init();
        curl_easy_setopt(curl, CURLOPT_URL, ("https://api.unsplash.com/photos/random?client_id=" + UNSPLASH_ACCESS_KEY).c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, [](char* ptr, size_t size, size_t nmemb, void* userdata) -> size_t {
            string* data = static_cast<string*>(userdata);
            data->append(ptr, size * nmemb);
            return size * nmemb;
        });
        string response_data;
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_data);
        curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        json response = json::parse(response_data);
        image_url = response["urls"]["full"].get<string>();
    } else if (source == "bing") {
        CURL* curl = curl_easy_init();
        curl_easy_setopt(curl, CURLOPT_URL, "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US");
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, [](char* ptr, size_t size, size_t nmemb, void* userdata) -> size_t {
            string* data = static_cast<string*>(userdata);
            data->append(ptr, size * nmemb);
            return size * nmemb;
        });
        string response_data;
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_data);
        curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        json response = json::parse(response_data);
        image_url = "https://www.bing.com" + response["images"][0]["url"].get<string>();
    } else if (source == "pexels") {
        CURL* curl = curl_easy_init();
        curl_easy_setopt(curl, CURLOPT_URL, "https://api.pexels.com/v1/curated");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, ("Authorization: " + PEXELS_API_KEY).c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, [](char* ptr, size_t size, size_t nmemb, void* userdata) -> size_t {
            string* data = static_cast<string*>(userdata);
            data->append(ptr, size * nmemb);
            return size * nmemb;
        });
        string response_data;
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_data);
        curl_easy_perform(curl);
        curl_easy_cleanup(curl);

        json response = json::parse(response_data);
        image_url = response["photos"][dis(gen)]["src"]["original"].get<string>();
    }

    CURL* curl = curl_easy_init();
    curl_easy_setopt(curl, CURLOPT_URL, image_url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, [](char* ptr, size_t size, size_t nmemb, void* userdata) -> size_t {
        ofstream* file = static_cast<ofstream*>(userdata);
        file->write(ptr, size * nmemb);
        return size * nmemb;
    });
    ofstream file(temp_folder + "\\wallpaper.bmp", ios::binary);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &file);
    curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    file.close();

    SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, (PVOID)(temp_folder + "\\wallpaper.bmp").c_str(), SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE);
    return temp_folder + "\\wallpaper.bmp";
}

void save_wallpaper(HICON icon, UINT item) {
    if (!current_wallpaper_path.empty()) {
        string base_name = filesystem::path(current_wallpaper_path).filename().string();
        string save_path = desired_folder + "\\" + base_name;
        CopyFileA(current_wallpaper_path.c_str(), save_path.c_str(), FALSE);
        cout << "Wallpaper saved to " << save_path << endl;
    }
}

void open_about(HICON icon, UINT item) {
    HINSTANCE hInstance = GetModuleHandle(NULL);
    HWND hWnd = CreateWindowEx(0, _T("STATIC"), _T("About"), WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 800, 600, NULL, NULL, hInstance, NULL);
    ShowWindow(hWnd, SW_SHOW);
    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}

void exit_application(HICON icon, UINT item) {
    Shell_NotifyIcon(NIM_DELETE, &nid);
    PostQuitMessage(0);
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    temp_folder = getenv("TEMP");
    char path[MAX_PATH];
    SHGetFolderPathA(NULL, CSIDL_PERSONAL, NULL, 0, path);
    desired_folder = string(path) + "\\Saved Wallpapers";
    CreateDirectoryA(desired_folder.c_str(), NULL);

    NOTIFYICONDATA nid = {0};
    nid.cbSize = sizeof(NOTIFYICONDATA);
    nid.hWnd = NULL;
    nid.uID = 0;
    nid.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP;
    nid.hIcon = create_image();
    nid.uCallbackMessage = WM_USER + 1;
    strcpy_s(nid.szTip, "Wallpaper Changer");
    Shell_NotifyIcon(NIM_ADD, &nid);

    MSG msg;
    while (GetMessage(&msg, NULL, 0, 0)) {
        if (msg.message == WM_USER + 1) {
            switch (msg.lParam) {
                case WM_RBUTTONUP:
                    POINT pt;
                    GetCursorPos(&pt);
                    HMENU hMenu = CreatePopupMenu();
                    AppendMenu(hMenu, MF_STRING, 1, "Next Wallpaper");
                    AppendMenu(hMenu, MF_STRING, 2, "Save Wallpaper");
                    AppendMenu(hMenu, MF_STRING, 3, "About");
                    AppendMenu(hMenu, MF_STRING, 4, "Exit");
                    SetForegroundWindow(nid.hWnd);
                    TrackPopupMenu(hMenu, TPM_RIGHTALIGN, pt.x, pt.y, 0, nid.hWnd, NULL);
                    DestroyMenu(hMenu);
                    break;
                case 1:
                    current_wallpaper_path = fetch_wallpaper();
                    break;
                case 2:
                    save_wallpaper(nid.hIcon, msg.lParam);
                    break;
                case 3:
                    open_about(nid.hIcon, msg.lParam);
                    break;
                case 4:
                    exit_application(nid.hIcon, msg.lParam);
                    break;
            }
        } else {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }

    return 0;
}

