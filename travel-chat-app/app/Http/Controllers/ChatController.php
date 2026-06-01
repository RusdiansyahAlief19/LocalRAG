<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ChatController extends Controller
{
    public function index()
    {
        return view('chat');
    }

    public function sendMessage(Request $request)
    {
        $request->validate([
            'query' => 'required|string'
        ]);

        try {
            // Forward the query to the Golang RAG service running in the same Docker network
            $response = Http::timeout(60)->post('http://rag-service:8080/api/ask', [
                'query' => $request->input('query')
            ]);

            if ($response->successful()) {
                return response()->json([
                    'answer' => $response->json('answer')
                ]);
            }

            return response()->json(['error' => 'Failed to reach AI service. Error: ' . $response->body()], $response->status());
        } catch (\Exception $e) {
            return response()->json(['error' => 'Connection to RAG Service failed: ' . $e->getMessage()], 500);
        }
    }

    public function uploadDocument(Request $request)
    {
        $request->validate([
            'document' => 'required|file|mimes:pdf,txt|max:10240',
        ]);

        try {
            $file = $request->file('document');
            $response = Http::timeout(120)->attach(
                'document', file_get_contents($file->getPathname()), $file->getClientOriginalName()
            )->post('http://rag-service:8080/api/process-document');

            if ($response->successful()) {
                return response()->json(['message' => 'Document processed successfully!']);
            }

            return response()->json(['error' => 'Failed to process document in RAG service. ' . $response->body()], $response->status());
        } catch (\Exception $e) {
            return response()->json(['error' => 'Connection to RAG Service failed: ' . $e->getMessage()], 500);
        }
    }
}
