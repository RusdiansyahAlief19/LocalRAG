<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ChatController;

Route::get('/', [ChatController::class, 'index']);
Route::post('/chat', [ChatController::class, 'sendMessage']);
Route::post('/upload', [ChatController::class, 'uploadDocument']);
