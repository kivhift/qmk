#include <windows.h>

typedef void (*hook_callback_t)(int);
typedef enum {
	qmk_up = 0,
	qmk_down
} qmk_state_t;

static DWORD qmk_code = VK_CAPITAL;
static qmk_state_t qmk_state = qmk_up;
static hook_callback_t kbhcb = (hook_callback_t) 0;
static HHOOK kb_hook = (HHOOK) 0;
static HINSTANCE dll_instance;

static LRESULT CALLBACK keyboard_callback(int hook_code, WPARAM msg_id,
	LPARAM msg_data)
{
	PKBDLLHOOKSTRUCT hs;
	int transition_up;

	if(HC_ACTION != hook_code) {
		goto call_next_hook;
	}

	hs = (PKBDLLHOOKSTRUCT) msg_data;

	if(qmk_code != hs->vkCode) {
		goto call_next_hook;
	}

	if(LLKHF_INJECTED & hs->flags) {
		goto call_next_hook;
	}

	transition_up = (int) LLKHF_UP & hs->flags;

	switch(qmk_state) {
	case qmk_up:
		if(!transition_up) {
			qmk_state = qmk_down;
			if(kbhcb) {
				(*kbhcb)(qmk_state);
			}
		}
		break;
	case qmk_down:
		if(transition_up) {
			qmk_state = qmk_up;
			if(kbhcb) {
				(*kbhcb)(qmk_state);
			}
		}
		break;
	default:
		break;
	}

	return 1;

call_next_hook:
	return CallNextHookEx(0, hook_code, msg_id, msg_data);
}

int install_keyboard_hook(void)
{
	HOOKPROC addr;
	addr = keyboard_callback;

	kb_hook = SetWindowsHookEx(WH_KEYBOARD_LL, addr, dll_instance, 0);
	if(!kb_hook) {
		return 1;
	}

	return 0;
}

void uninstall_keyboard_hook(void)
{
	if(kb_hook) {
		UnhookWindowsHookEx(kb_hook);
		kb_hook = (HHOOK) 0;
	}
}

void set_keyboard_hook_callback(hook_callback_t cb)
{
	kbhcb = cb;
}

void inject_press_and_release(void)
{
	keybd_event((BYTE) qmk_code, 0, 0, 0);
	keybd_event((BYTE) qmk_code, 0, KEYEVENTF_KEYUP, 0);
}

int set_key_code(DWORD code)
{
	if((code < 1) || (code > 254)) {
		return 1;
	}

	qmk_code = code;

	return 0;
}

BOOL WINAPI DllMain(HINSTANCE HI, DWORD reason, LPVOID reserved)
{
	switch(reason) {
	case DLL_PROCESS_ATTACH:
		dll_instance = HI;
		break;
	case DLL_PROCESS_DETACH:
		uninstall_keyboard_hook();
		break;
	default:
		break;
	}

	return TRUE;
}
