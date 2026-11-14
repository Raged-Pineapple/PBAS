<?php
/**
 * PBAS API Client for PHP Integration
 * Allows PHP code to interact seamlessly with the Django / Python PBAS API backend.
 */

class PBASApiClient {
    private string $baseUrl;
    private int $timeout;

    public function __construct(string $baseUrl = 'http://127.0.0.1:8000', int $timeout = 10) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeout = $timeout;
    }

    /**
     * Send Section 1 data to Django API for calculation
     */
    public function calculateSection1(array $data): array {
        $url = $this->baseUrl . '/api/section1/calculate/';
        $jsonData = json_encode($data);

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Content-Length: ' . strlen($jsonData)
        ]);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);

        if ($error) {
            throw new Exception("PBAS API cURL Error: " . $error);
        }

        if ($httpCode >= 400) {
            throw new Exception("PBAS API HTTP Error ($httpCode): " . $response);
        }

        return json_decode($response, true) ?: [];
    }

    /**
     * Upload an evidence file to PBAS backend
     */
    public function uploadEvidence(string $filePath, string $componentCode): array {
        $url = $this->baseUrl . '/api/upload/';
        $cFile = new CURLFile(realpath($filePath));

        $postFields = [
            'file' => $cFile,
            'component' => $componentCode
        ];

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode >= 400) {
            throw new Exception("Upload failed ($httpCode): " . $response);
        }

        return json_decode($response, true) ?: [];
    }
}
