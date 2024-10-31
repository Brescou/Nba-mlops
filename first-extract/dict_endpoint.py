nba_endpoints_player = {
    "player_bios": {
        "url": "playerindex",
        "params": {
            "LeagueID": "00",
            "Season": "2024-25",
            "Historical": 1,
            "TeamID": 0,
            "Country": "",
            "College": "",
            "DraftPick": "",
            "DraftRound": "",
            "DraftYear": "",
            "Height": "",
            "Weight": ""
        }
    },
    "general": {
        "traditional": {
            "url": "leaguedashplayerstats",
            "params": {
                "MeasureType": "Base",
                "Season": None,
                "SeasonType": None,
            }
        },
        "advanced": {
            "url": "leaguedashplayerstats",
            "params": {
                "MeasureType": "Advanced",
                "Season": None,
                "SeasonType": None,
            }
        },
        "misc": {
            "url": "leaguedashplayerstats",
            "params": {
                "MeasureType": "Misc",
                "Season": None,
                "SeasonType": None,
            }
        },
        "scoring": {
            "url": "leaguedashplayerstats",
            "params": {
                "MeasureType": "Scoring",
                "Season": None,
                "SeasonType": None,
            }
        },
        "usage": {
            "url": "leaguedashplayerstats",
            "params": {
                "MeasureType": "Usage",
                "Season": None,
                "SeasonType": None,
            }
        }
    },
    "clutch": {
        "traditional": {
            "url": "leaguedashplayerclutch",
            "params": {
                "MeasureType": "Base",
                "Season": None,
                "SeasonType": None,
            }
        },
        "advanced": {
            "url": "leaguedashplayerclutch",
            "params": {
                "MeasureType": "Advanced",
                "Season": None,
                "SeasonType": None,
            }
        }
    },
    "playtype": {
        "isolation": {
            "url": "synergyplaytypes",
            "params": {
                "PlayType": "Isolation",
                "SeasonYear": None,
                "SeasonType": None,
            }
        },
        "pick_roll_ball_handler": {
            "url": "synergyplaytypes",
            "params": {
                "PlayType": "PRBallHandler",
                "SeasonYear": None,
                "SeasonType": None,
            }
        }
    },
    "tracking": {
        "drives": {
            "url": "leaguedashptstats",
            "params": {
                "PtMeasureType": "Drives",
                "Season": None,
                "SeasonType": None,
            }
        },
        "defensive_impact": {
            "url": "leaguedashptstats",
            "params": {
                "PtMeasureType": "Defense",
                "Season": None,
                "SeasonType": None,
            }
        },
        "catch_shoot": {
            "url": "leaguedashptstats",
            "params": {
                "PtMeasureType": "CatchShoot",
                "Season": None,
                "SeasonType": None,
            }
        }
    },
    "defense_dashboard": {
        "overall": {
            "url": "leaguedashptdefend",
            "params": {
                "DefenseCategory": "Overall",
                "Season": None,
                "SeasonType": None,
            }
        }
    }
}
nba_endpoints_teams = {
    "general": {
        "traditional": {
            "url": "leaguedashteamstats",
            "params": {
                "MeasureType": "Base",
                "Season": None,
                "SeasonType": None,
            }
        },
        "advanced": {
            "url": "leaguedashteamstats",
            "params": {
                "MeasureType": "Advanced",
                "Season": None,
                "SeasonType": None,
            }
        },
        "misc": {
            "url": "leaguedashteamstats",
            "params": {
                "MeasureType": "Misc",
                "Season": None,
                "SeasonType": None,
            }
        },
        "scoring": {
            "url": "leaguedashteamstats",
            "params": {
                "MeasureType": "Scoring",
                "Season": None,
                "SeasonType": None,
            }
        }
    },
    "clutch": {
        "traditional": {
            "url": "leaguedashteamclutch",
            "params": {
                "MeasureType": "Base",
                "Season": None,
                "SeasonType": None,
            }
        }
    },
    "tracking": {
        "drives": {
            "url": "leaguedashptstats",
            "params": {
                "PtMeasureType": "Drives",
                "Season": None,
                "SeasonType": None,
            }
        },
        "defensive_impact": {
            "url": "leaguedashptstats",
            "params": {
                "PtMeasureType": "Defense",
                "Season": None,
                "SeasonType": None,
            }
        },
        "catch_shoot": {
            "url": "leaguedashptstats",
            "params": {
                "PtMeasureType": "CatchShoot",
                "Season": None,
                "SeasonType": None,
            }
        }
    },
    "defense_dashboard": {
        "overall": {
            "url": "leaguedashptteamdefend",
            "params": {
                "DefenseCategory": "Overall",
                "Season": None,
                "SeasonType": None,
            }
        }
    }
}
nba_endpoints_lineups = {
    "traditional": {
        "url": "leaguedashlineups",
        "params": {
            "MeasureType": "Base",
            "Season": None,
            "SeasonType": None,
            "GroupQuantity": 5
        }
    },
    "advanced": {
        "url": "leaguedashlineups",
        "params": {
            "MeasureType": "Advanced",
            "Season": None,
            "SeasonType": None,
            "GroupQuantity": 5
        }
    },
    "misc": {
        "url": "leaguedashlineups",
        "params": {
            "MeasureType": "Misc",
            "Season": None,
            "SeasonType": None,
            "GroupQuantity": 5
        }
    },
    "four_factors": {
        "url": "leaguedashlineups",
        "params": {
            "MeasureType": "Four Factors",
            "Season": None,
            "SeasonType": None,
            "GroupQuantity": 5
        }
    },
    "scoring": {
        "url": "leaguedashlineups",
        "params": {
            "MeasureType": "Scoring",
            "Season": None,
            "SeasonType": None,
            "GroupQuantity": 5
        }
    },
    "opponent": {
        "url": "leaguedashlineups",
        "params": {
            "MeasureType": "Opponent",
            "Season": None,
            "SeasonType": None,
            "GroupQuantity": 5
        }
    }
}
nba_endpoints_games = {
    "game_log": {
        "url": "leaguegamelog",
        "params": {
            "Counter": "1000",
            "DateFrom": "",
            "DateTo": "",
            "Direction": "DESC",
            "ISTRound": "",
            "LeagueID": "00",
            "PlayerOrTeam": "T",
            "Season": None,
            "SeasonType": None,
            "Sorter": "DATE"
        }
    },
    "play_by_play": {
        "url": "playbyplayv3",
        "params": {
            "GameID": None,
            "StartPeriod": "0",
            "EndPeriod": "0"
        }
    }
}
