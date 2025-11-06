#pragma once

#include "GuiBase.h"
#include "bakkesmod/plugin/bakkesmodplugin.h"
#include "bakkesmod/plugin/pluginwindow.h"
#include "bakkesmod/plugin/PluginSettingsWindow.h"

#include "version.h"

#include "libs/httplib.h"
#include <thread>
#include <atomic>
#include <memory>
#include <functional>

constexpr auto plugin_version = stringify(VERSION_MAJOR) "." stringify(VERSION_MINOR) "." stringify(VERSION_PATCH) "." stringify(VERSION_BUILD);


class RLHighlightMaker: public BakkesMod::Plugin::BakkesModPlugin
	//,public SettingsWindowBase // Uncomment if you wanna render your own tab in the settings menu
	//,public PluginWindowBase // Uncomment if you want to render your own plugin window
{
private:
	// Server
	std::unique_ptr<httplib::Server> svr;
	std::thread server_thread;
	void startServer();
	void stopServer();

	void executeOnGameThread(std::function<void(GameWrapper*)> func);

	//Boilerplate
	void onLoad() override;
	void onUnload() override; 

public:
	//void RenderSettings() override; // Uncomment if you wanna render your own tab in the settings menu
	//void RenderWindow() override; // Uncomment if you want to render your own plugin window
};
