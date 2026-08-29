/**
 * Tomer & Shuki Daily Chess Backend
 * Spreadsheet ID: 10_2IyVfyPUW5Fm2IuW0xCa-XKDotfm6jXcIH9-th5Ew
 */

const SPREADSHEET_ID = '10_2IyVfyPUW5Fm2IuW0xCa-XKDotfm6jXcIH9-th5Ew';

function doGet(e) {
  const template = HtmlService.createTemplateFromFile('index');
  const htmlOutput = template.evaluate()
    .setTitle('שחמט - תומר ושוקי')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
  return htmlOutput;
}

function getSpreadsheet() {
  return SpreadsheetApp.openById(SPREADSHEET_ID);
}

function getGameState() {
  const ss = getSpreadsheet();
  const stateSheet = ss.getSheetByName('GameState');
  const values = stateSheet.getDataRange().getValues();

  const state = {};
  for (let i = 1; i < values.length; i++) {
    const key = values[i][0];
    const val = values[i][1];
    if (key) {
      state[key] = val;
    }
  }

  // Retrieve move history
  const historySheet = ss.getSheetByName('MoveHistory');
  const history = [];
  if (historySheet && historySheet.getLastRow() > 1) {
    const histValues = historySheet.getDataRange().getValues();
    for (let i = 1; i < histValues.length; i++) {
      if (histValues[i][0] !== '') {
        history.push({
          moveNumber: histValues[i][0],
          player: histValues[i][1],
          san: histValues[i][2],
          uci: histValues[i][3],
          fenAfter: histValues[i][4],
          timestamp: histValues[i][5]
        });
      }
    }
  }
  state.history = history;
  return state;
}

function recordMove(moveData) {
  // moveData: { player: 'tomer' | 'shuki', from: 'e2', to: 'e4', san: 'e4', uci: 'e2e4', fenAfter: '...', isGameOver: false, result: '' }
  const ss = getSpreadsheet();
  const stateSheet = ss.getSheetByName('GameState');
  const historySheet = ss.getSheetByName('MoveHistory');

  const state = getGameState();
  const nextTurn = (moveData.player === 'tomer') ? state.shuki_color : state.tomer_color;
  const newCount = (parseInt(state.move_count, 10) || 0) + 1;
  const nowStr = new Date().toISOString();

  // Update GameState sheet
  const rows = [
    ['Key', 'Value'],
    ['status', moveData.isGameOver ? (moveData.result || 'finished') : 'active'],
    ['fen', moveData.fenAfter],
    ['turn', nextTurn],
    ['tomer_color', state.tomer_color || 'w'],
    ['shuki_color', state.shuki_color || 'b'],
    ['last_move', moveData.san || moveData.uci],
    ['last_move_by', moveData.player],
    ['last_move_time', nowStr],
    ['pgn', (state.pgn ? state.pgn + ' ' : '') + (moveData.san || moveData.uci)],
    ['move_count', newCount]
  ];

  stateSheet.getRange(1, 1, rows.length, 2).setValues(rows);

  // Append to MoveHistory sheet
  historySheet.appendRow([
    newCount,
    moveData.player,
    moveData.san || moveData.uci,
    moveData.uci,
    moveData.fenAfter,
    nowStr
  ]);

  return {
    success: true,
    gameState: getGameState()
  };
}

function resetGame(tomerColor) {
  tomerColor = tomerColor === 'b' ? 'b' : 'w';
  const shukiColor = tomerColor === 'w' ? 'b' : 'w';
  const initialFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
  const nowStr = new Date().toISOString();

  const ss = getSpreadsheet();
  const stateSheet = ss.getSheetByName('GameState');
  const historySheet = ss.getSheetByName('MoveHistory');

  const rows = [
    ['Key', 'Value'],
    ['status', 'active'],
    ['fen', initialFen],
    ['turn', 'w'],
    ['tomer_color', tomerColor],
    ['shuki_color', shukiColor],
    ['last_move', ''],
    ['last_move_by', ''],
    ['last_move_time', nowStr],
    ['pgn', ''],
    ['move_count', 0]
  ];

  stateSheet.clearContents();
  stateSheet.getRange(1, 1, rows.length, 2).setValues(rows);

  historySheet.clearContents();
  historySheet.appendRow(['MoveNumber', 'Player', 'MoveSAN', 'MoveUCI', 'FenAfter', 'Timestamp']);

  return {
    success: true,
    gameState: getGameState()
  };
}
