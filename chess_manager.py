#!/usr/bin/env python3
"""
Tomer & Shuki Chess Management Script
Handles board state, move calculations, delay enforcement, and Google Sheets sync.
"""

import sys
import json
import random
import datetime
import subprocess
import chess

SPREADSHEET_ID = "10_2IyVfyPUW5Fm2IuW0xCa-XKDotfm6jXcIH9-th5Ew"
GWS_BIN = "/home/opc/mcp-servers/shuki-local-tools/node_modules/.bin/gws"

def run_gws(service, resource, sub_resource, method, params=None, body=None):
    cmd = [GWS_BIN, service, resource]
    if sub_resource:
        cmd.append(sub_resource)
    cmd.append(method)
    if params:
        cmd.extend(["--params", json.dumps(params)])
    if body:
        cmd.extend(["--json", json.dumps(body)])

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"GWS error ({res.returncode}): {res.stderr.strip() or res.stdout.strip()}")
    return json.loads(res.stdout)

def get_game_state():
    params = {
        "spreadsheetId": SPREADSHEET_ID,
        "range": "GameState!A1:B11"
    }
    res = run_gws("sheets", "spreadsheets", "values", "get", params=params)
    values = res.get("values", [])
    state = {}
    for row in values[1:]:
        if len(row) >= 2:
            state[row[0]] = row[1]
        elif len(row) == 1:
            state[row[0]] = ""
    return state

def update_game_state(state_dict):
    rows = [
        ["Key", "Value"],
        ["status", state_dict.get("status", "active")],
        ["fen", state_dict.get("fen", chess.STARTING_FEN)],
        ["turn", state_dict.get("turn", "w")],
        ["tomer_color", state_dict.get("tomer_color", "w")],
        ["shuki_color", state_dict.get("shuki_color", "b")],
        ["last_move", state_dict.get("last_move", "")],
        ["last_move_by", state_dict.get("last_move_by", "")],
        ["last_move_time", state_dict.get("last_move_time", "")],
        ["pgn", state_dict.get("pgn", "")],
        ["move_count", str(state_dict.get("move_count", "0"))]
    ]
    params = {
        "spreadsheetId": SPREADSHEET_ID,
        "range": "GameState!A1:B11",
        "valueInputOption": "RAW"
    }
    body = {
        "values": rows
    }
    return run_gws("sheets", "spreadsheets", "values", "update", params=params, body=body)

def append_move_history(move_number, player, san, uci, fen_after, timestamp):
    params = {
        "spreadsheetId": SPREADSHEET_ID,
        "range": "MoveHistory!A1:F1",
        "valueInputOption": "RAW"
    }
    body = {
        "values": [
            [move_number, player, san, uci, fen_after, timestamp]
        ]
    }
    return run_gws("sheets", "spreadsheets", "values", "append", params=params, body=body)

def evaluate_board_amateur(board, shuki_color):
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 310,
        chess.BISHOP: 320,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    val = 0
    for square, piece in board.piece_map().items():
        score = piece_values.get(piece.piece_type, 0)
        # Center control bonus
        if square in [chess.D4, chess.D5, chess.E4, chess.E5]:
            score += 20
        elif square in [chess.C3, chess.C4, chess.C5, chess.C6, chess.D3, chess.D6, chess.E3, chess.E6, chess.F3, chess.F4, chess.F5, chess.F6]:
            score += 10

        if piece.color == shuki_color:
            val += score
        else:
            val -= score
    return val

def choose_shuki_move(board, shuki_color):
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    # Check for immediate win or strong tactical responses
    scored_moves = []
    for move in legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return move

        score = evaluate_board_amateur(board, shuki_color)
        opp_moves = list(board.legal_moves)
        if opp_moves:
            worst_for_shuki = min([
                (board.push(opp_m), evaluate_board_amateur(board, shuki_color), board.pop())[1]
                for opp_m in opp_moves[:12]
            ])
            score = (score + worst_for_shuki) / 2

        board.pop()
        scored_moves.append((score, move))

    scored_moves.sort(key=lambda x: x[0], reverse=True)

    # Pick randomly from the top 3 moves to maintain amateur natural feel
    top_n = scored_moves[:min(3, len(scored_moves))]
    chosen = random.choice(top_n)[1]
    return chosen

def play_shuki_turn(force=False):
    state = get_game_state()
    fen = state.get("fen", chess.STARTING_FEN)
    turn = state.get("turn", "w")
    shuki_color_str = state.get("shuki_color", "b")
    shuki_color = chess.WHITE if shuki_color_str == "w" else chess.BLACK
    tomer_color_str = state.get("tomer_color", "w")

    if turn != shuki_color_str:
        return {"status": "waiting_for_tomer", "message": "It is Tomer's turn."}

    board = chess.Board(fen)
    if board.is_game_over():
        return {"status": "game_over", "result": board.result()}

    move = choose_shuki_move(board, shuki_color)
    if not move:
        return {"status": "no_legal_moves"}

    san = board.san(move)
    uci = move.uci()
    board.push(move)
    new_fen = board.fen()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    new_count = int(state.get("move_count", 0)) + 1

    is_over = board.is_game_over()
    status = "finished" if is_over else "active"
    if board.is_checkmate():
        status = "checkmate"
    elif board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        status = "draw"

    new_pgn = (state.get("pgn", "") + " " + san).strip()

    new_state = {
        "status": status,
        "fen": new_fen,
        "turn": tomer_color_str,
        "tomer_color": tomer_color_str,
        "shuki_color": shuki_color_str,
        "last_move": san,
        "last_move_by": "shuki",
        "last_move_time": now_str,
        "pgn": new_pgn,
        "move_count": new_count
    }

    update_game_state(new_state)
    append_move_history(new_count, "shuki", san, uci, new_fen, now_str)

    return {
        "status": "success",
        "move": san,
        "uci": uci,
        "fen": new_fen,
        "game_over": is_over,
        "next_turn": tomer_color_str
    }

def reset_game(tomer_color="w"):
    tomer_color = "b" if tomer_color == "b" else "w"
    shuki_color = "w" if tomer_color == "b" else "b"
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    new_state = {
        "status": "active",
        "fen": chess.STARTING_FEN,
        "turn": "w",
        "tomer_color": tomer_color,
        "shuki_color": shuki_color,
        "last_move": "",
        "last_move_by": "",
        "last_move_time": now_str,
        "pgn": "",
        "move_count": "0"
    }

    update_game_state(new_state)

    # Clear MoveHistory and set header
    params_clear = {
        "spreadsheetId": SPREADSHEET_ID,
        "range": "MoveHistory!A1:F1000"
    }
    try:
        run_gws("sheets", "spreadsheets", "values", "clear", params=params_clear)
    except Exception:
        pass

    params_head = {
        "spreadsheetId": SPREADSHEET_ID,
        "range": "MoveHistory!A1:F1",
        "valueInputOption": "RAW"
    }
    body_head = {
        "values": [["MoveNumber", "Player", "MoveSAN", "MoveUCI", "FenAfter", "Timestamp"]]
    }
    run_gws("sheets", "spreadsheets", "values", "update", params=params_head, body=body_head)

    return {"status": "reset_done", "state": new_state}

def watch_game(interval=4):
    import time
    print(f"Starting Shuki Chess Watcher (interval={interval}s)...")
    while True:
        try:
            state = get_game_state()
            status = state.get("status", "active")
            turn = state.get("turn", "w")
            shuki_color = state.get("shuki_color", "b")
            last_move_by = state.get("last_move_by", "")

            if status == "active" and turn == shuki_color and last_move_by != "shuki":
                res = play_shuki_turn(force=True)
                if res.get("status") == "success":
                    print(f"[{datetime.datetime.now().isoformat()}] Shuki played {res.get('move')} ({res.get('uci')})")
        except Exception as e:
            print(f"[{datetime.datetime.now().isoformat()}] Watcher error: {e}", file=sys.stderr)

        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "status":
        st = get_game_state()
        print(json.dumps(st, ensure_ascii=False, indent=2))
    elif sys.argv[1] == "move":
        force = "--force" in sys.argv
        res = play_shuki_turn(force=force)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif sys.argv[1] == "reset":
        t_col = "w"
        if len(sys.argv) > 2 and sys.argv[2] in ["w", "b"]:
            t_col = sys.argv[2]
        res = reset_game(tomer_color=t_col)
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif sys.argv[1] == "watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
        watch_game(interval=interval)
