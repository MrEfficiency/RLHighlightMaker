#include "pch.h"
#include "RLHighlightMaker.h"
#include "GameWindowFocuser.h"
#include "libs/nlohmann/json.hpp"

#include "bakkesmod/wrappers/GameObject/ReplayManagerWrapper.h"
//#include "bakkesmod/wrappers/ReplayWrapper.h"
#include "bakkesmod/wrappers/GameEvent/ReplaySoccarWrapper.h"
#include "bakkesmod/wrappers/ReplayViewerDataWrapper.h"
#include <future>

using json = nlohmann::json;

BAKKESMOD_PLUGIN(RLHighlightMaker, "Plugin to externally manipulate Rocket League replays", plugin_version, PLUGINTYPE_REPLAY)

std::shared_ptr<CVarManagerWrapper> _globalCvarManager;

void RLHighlightMaker::onLoad()
{
	_globalCvarManager = cvarManager;
	this->startServer();
}

void RLHighlightMaker::onUnload()
{
	this->stopServer();
}

void RLHighlightMaker::executeOnGameThread(std::function<void(GameWrapper*)> func)
{
	gameWrapper->Execute(func);
}

void RLHighlightMaker::startServer()
{
	svr = std::make_unique<httplib::Server>();

	svr->Get("/status", [this](const httplib::Request& req, httplib::Response& res) {
		res.set_content("{\"status\": \"ready\"}", "application/json");
		LOG("Checking status");
	});

	svr->Post("/focus", [this](const httplib::Request& req, httplib::Response& res) {
		cvarManager->log("Focus endpoint hit");
		GameWindowFocuser::MoveGameToFront();
		res.set_content("{\"status\": \"focused\"}", "application/json");
	});

	svr->Post("/load_replay", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			std::string path = body.at("path");
			LOG("Attempting to load replay with path {}", path);
			cvarManager->log("Loading replay: " + path);
			executeOnGameThread([this, path](GameWrapper* gw) {
				gw->GetReplayManagerWrapper().PlayReplayFile(path);
			});
			res.set_content("{\"status\": \"loading replay\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});

	svr->Get("/replay/highlights", [this](const httplib::Request& req, httplib::Response& res) {
		std::promise<json> promise;
		std::future<json> future = promise.get_future();

		cvarManager->log("[/replay/highlights] Request received, executing on game thread...");
		executeOnGameThread([this, &promise, &res](GameWrapper* gw) {
			cvarManager->log("[/replay/highlights] Inside game thread lambda.");
			try {
				if (!gw->IsInReplay()) {
					res.status = 404;
					promise.set_value(json({{"error", "Not in a replay"}}));
					cvarManager->log("[/replay/highlights] Not in a replay.");
					return;
				}

				auto replayManager = gw->GetReplayManagerWrapper();
				if (!replayManager) {
					res.status = 500;
					promise.set_value(json({{"error", "Could not get replay manager"}}));
					cvarManager->log("[/replay/highlights] Could not get replay manager.");
					return;
				}

				auto replays = replayManager.GetLoadedReplays();
				if (replays.empty()) {
					res.status = 404;
					promise.set_value(json({{"error", "No loaded replays found"}}));
					cvarManager->log("[/replay/highlights] No loaded replays found.");
					return;
				}

				// Assumption: The first replay in the list is the active one.
				ReplaySoccarWrapper replaySoccar = replays.at(0);

				json highlights = json::array();
				for (const auto& goal : replaySoccar.GetGoals()) {
					highlights.push_back(goal.frame);
				}
				promise.set_value(highlights);
				cvarManager->log("[/replay/highlights] Highlights data prepared.");
			} catch (const std::exception& e) {
				cvarManager->log("[/replay/highlights] Exception in game thread lambda: " + std::string(e.what()));
				res.status = 500;
				promise.set_value(json({{"error", "Internal server error: " + std::string(e.what())}}));
			}
		});

		try {
			json highlights_json = future.get(); // Wait for the result from the game thread
			res.set_content(highlights_json.dump(), "application/json");
			cvarManager->log("[/replay/highlights] Response sent: " + highlights_json.dump());
		} catch (const std::exception& e) {
			cvarManager->log("[/replay/highlights] Exception while getting future or setting response: " + std::string(e.what()));
			res.status = 500;
			res.set_content("{\"error\": \"Internal server error: " + std::string(e.what()) + "\"}", "application/json");
		}
	});

	svr->Post("/replay/seek", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			int frame = body.at("frame");
			executeOnGameThread([this, frame](GameWrapper* gw) {
				if (!gw->IsInReplay()) return;
				auto replayWrapper = gw->GetGameEventAsReplay();
				if (!replayWrapper) return;
				replayWrapper.SkipToFrame(frame);
			});
			res.set_content("{\"status\": \"seeked\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});

	svr->Post("/replay/slomo", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			float slomo = body.at("slomo");
			executeOnGameThread([this, slomo](GameWrapper* gw) {
				if (!gw->IsInReplay()) return;
				SpectatorHUDWrapper specHud = gw->GetPlayerController().GetSpectatorHud();
				if (!specHud.IsNull()) {
					ReplayViewerDataWrapper replayViewer = specHud.GetViewerData();
					if (!replayViewer.IsNull()) {
						replayViewer.SetSlomo(slomo);
					}
				}
			});
			res.set_content("{\"status\": \"slomo set to " + std::to_string(slomo) + "\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});

	svr->Post("/replay/player_names", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			bool enabled = body.at("enabled");
			executeOnGameThread([this, enabled](GameWrapper* gw) {
				if (!gw->IsInReplay()) return;
				SpectatorHUDWrapper specHud = gw->GetPlayerController().GetSpectatorHud();
				if (!specHud.IsNull()) {
					ReplayViewerDataWrapper replayViewer = specHud.GetViewerData();
					if (!replayViewer.IsNull()) {
						replayViewer.SetShowPlayerNames(enabled);
					}
				}
			});
			res.set_content("{\"status\": \"player names visibility set to " + std::string(enabled ? "true" : "false") + "\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});

	svr->Post("/replay/match_info_hud", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			bool enabled = body.at("enabled");
			executeOnGameThread([this, enabled](GameWrapper* gw) {
				if (!gw->IsInReplay()) return;
				SpectatorHUDWrapper specHud = gw->GetPlayerController().GetSpectatorHud();
				if (!specHud.IsNull()) {
					ReplayViewerDataWrapper replayViewer = specHud.GetViewerData();
					if (!replayViewer.IsNull()) {
						replayViewer.SetShowMatchInfoHUD(enabled);
					}
				}
			});
			res.set_content("{\"status\": \"match info HUD visibility set to " + std::string(enabled ? "true" : "false") + "\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});

	svr->Post("/replay/replay_hud", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			bool enabled = body.at("enabled");
			executeOnGameThread([this, enabled](GameWrapper* gw) {
				if (!gw->IsInReplay()) return;
				SpectatorHUDWrapper specHud = gw->GetPlayerController().GetSpectatorHud();
				if (!specHud.IsNull()) {
					ReplayViewerDataWrapper replayViewer = specHud.GetViewerData();
					if (!replayViewer.IsNull()) {
						replayViewer.SetShowReplayHUD(enabled);
					}
				}
			});
			res.set_content("{\"status\": \"replay HUD visibility set to " + std::string(enabled ? "true" : "false") + "\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});

	svr->Get("/replay/is_in_replay", [this](const httplib::Request& req, httplib::Response& res) {
		std::promise<bool> promise;
		std::future<bool> future = promise.get_future();

		cvarManager->log("[/replay/is_in_replay] Request received, executing on game thread...");
		executeOnGameThread([this, &promise](GameWrapper* gw) {
			cvarManager->log("[/replay/is_in_replay] Inside game thread lambda.");
			bool inReplay = false;
			try {
				inReplay = gw->IsInReplay();
				cvarManager->log("[/replay/is_in_replay] IsInReplay() returned: " + std::string(inReplay ? "true" : "false"));
			} catch (const std::exception& e) {
				cvarManager->log("[/replay/is_in_replay] Exception in IsInReplay(): " + std::string(e.what()));
			}
			promise.set_value(inReplay);
			cvarManager->log("[/replay/is_in_replay] Promise set_value called.");
		});

		try {
			bool inReplay = future.get(); // Wait for the result from the game thread
			std::string json_response = "{\"is_in_replay\": " + std::string(inReplay ? "true" : "false") + "}";
			res.set_content(json_response, "application/json");
			cvarManager->log("[/replay/is_in_replay] Response sent: " + json_response);
		} catch (const std::exception& e) {
			cvarManager->log("[/replay/is_in_replay] Exception while getting future or setting response: " + std::string(e.what()));
			res.status = 500;
			res.set_content("{\"error\": \"Internal server error: " + std::string(e.what()) + "\"}", "application/json");
		}
	});
	
	svr->Post("/camera/player", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			int team = body.at("team");
			int player = body.at("player");
			executeOnGameThread([this, team, player](GameWrapper* gw) {
				if (!gw->IsInReplay()) return;
				SpectatorHUDWrapper specHud = gw->GetPlayerController().GetSpectatorHud();
				if (!specHud.IsNull()) {
					specHud.ViewPlayer(team, player);
				}
			});
			res.set_content("{\"status\": \"viewing player\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});
	
	svr->Post("/camera/mode", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			std::string mode = body.at("mode");
			executeOnGameThread([this, mode](GameWrapper* gw) {
				if (!gw->IsInReplay()) return;
				SpectatorHUDWrapper specHud = gw->GetPlayerController().GetSpectatorHud();
				if (!specHud.IsNull()) {
					if (mode == "fly") {
						specHud.ViewFly();
					} else if (mode == "auto") {
						specHud.ViewAutoCam();
					} else if (mode == "default") {
						specHud.ViewDefault();
					}
				}
			});
			res.set_content("{\"status\": \"camera mode set to " + mode + "\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});
	
	svr->Post("/camera/focus_actor", [this](const httplib::Request& req, httplib::Response& res) {
		try {
			json body = json::parse(req.body);
			std::string actor_string = body.at("actor_string");
			executeOnGameThread([this, actor_string](GameWrapper* gw) {
				if (!gw->IsInReplay()) return;
				SpectatorHUDWrapper specHud = gw->GetPlayerController().GetSpectatorHud();
				if (!specHud.IsNull()) {
					specHud.SetFocusActorString(actor_string);
				}
			});
			res.set_content("{\"status\": \"focus set to " + actor_string + "\"}", "application/json");
		}
		catch (json::exception& e) {
			res.status = 400;
			res.set_content(std::string("{\"error\": \"Malformed JSON: ") + e.what() + "\"}", "application/json");
		}
	});
	
	server_thread = std::thread([this]() {
		cvarManager->log("RLHighlightMaker server starting on port 8080");
		if (!svr->listen("localhost", 8080))
		{
			cvarManager->log("RLHighlightMaker server failed to start!");
		}
	});}

void RLHighlightMaker::stopServer()
{
	if (svr && svr->is_running()) {
		svr->stop();
	}

	if (server_thread.joinable()) {
		server_thread.join();
	}
}
