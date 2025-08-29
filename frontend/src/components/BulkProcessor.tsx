import React, { useState, useCallback } from "react";
import FileUpload from "./FileUpload";
import Spinner from "./Spinner";
import { uploadAndProcessFile } from "../service/service";
import { ManualValidatorProps } from "../props";

const BulkProcessor: React.FC<ManualValidatorProps> = ({ memory }) => {
  // State for PDF to Excel Converter
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isConvertingPdf, setIsConvertingPdf] = useState(false);
  const [convertedExcelUrl, setConvertedExcelUrl] = useState<string | null>(
    null
  );
  const [pdfError, setPdfError] = useState<string | null>(null);

  // State for Excel Feature Analyser
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [isProcessingExcel, setIsProcessingExcel] = useState(false);
  const [processedExcelUrl, setProcessedExcelUrl] = useState<string | null>(
    null
  );
  const [excelError, setExcelError] = useState<string | null>(null);

  // --- Handlers for Excel Analyser ---
  const handleExcelSelect = useCallback(
    (file: File) => {
      setExcelFile(file);
      setExcelError(null);
      if (processedExcelUrl) {
        URL.revokeObjectURL(processedExcelUrl);
        setProcessedExcelUrl(null);
      }
    },
    [processedExcelUrl]
  );

  const handleExcelProcessing = async () => {
        if (!excelFile) {
          setExcelError('Please upload an Excel file.');
          return;
        }
        setIsProcessingExcel(true);
        setExcelError(null);
        try {
          const processedBlob = await uploadAndProcessFile(excelFile, memory);
          const url = URL.createObjectURL(processedBlob);
          setProcessedExcelUrl(url);
        } catch (err) {
          setExcelError(err instanceof Error ? err.message : 'Excel processing failed.');
        } finally {
          setIsProcessingExcel(false);
        }
  };

  const resetExcelAnalyser = () => {
    setExcelFile(null);
    if (processedExcelUrl) {
      URL.revokeObjectURL(processedExcelUrl);
    }
    setProcessedExcelUrl(null);
    setExcelError(null);
  };

  const actionButtonClasses =
    "mt-4 w-full flex justify-center items-center bg-cyan-400 text-black font-bold py-2 px-4 rounded-md hover:bg-cyan-500 disabled:bg-slate-700 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors";

  return (
    <div className="bg-slate-900 p-6 sm:p-8 rounded-xl border border-slate-700 max-w-3xl mx-auto">
      <h2 className="text-xl font-semibold text-slate-100">
        Batch Feature Processing Tools
      </h2>

      {/* Section 2: Excel Feature Analyser */}
      <div className="mt-8 border-t border-slate-700 pt-6">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-slate-100">
            Excel Feature Analyser
          </h3>
          <button
            onClick={resetExcelAnalyser}
            className="text-sm text-cyan-400 hover:underline disabled:text-slate-600 disabled:no-underline disabled:cursor-not-allowed"
            disabled={isProcessingExcel}
          >
            Reset
          </button>
        </div>
        <p className="mt-1 text-sm text-slate-400">
          Upload an Excel file (e.g., from the converter above) to Analyse all
          feature descriptions in bulk.
        </p>

        {!processedExcelUrl && (
          <div className="mt-4">
            <FileUpload
              acceptedFileTypes=".xlsx, .xls"
              onFileSelect={handleExcelSelect}
            />
            {excelFile && (
              <p className="mt-2 text-sm text-center text-slate-400">
                Selected: {excelFile.name}
              </p>
            )}
            <button
              onClick={handleExcelProcessing}
              disabled={!excelFile || isProcessingExcel}
              className={actionButtonClasses}
            >
              {isProcessingExcel ? <Spinner /> : "Analyse Excel File"}
            </button>
          </div>
        )}

        {excelError && (
          <div className="mt-4 text-red-300 bg-red-900/50 p-3 rounded-md border border-red-500/50">
            {excelError}
          </div>
        )}

        {processedExcelUrl && (
          <div className="mt-4 text-center p-4 bg-green-900/40 rounded-lg border border-green-500/30">
            <h4 className="font-semibold text-green-300">Analysis Complete!</h4>
            <a
              href={processedExcelUrl}
              download={`processed_${excelFile?.name || "features.xlsx"}`}
              className="mt-2 inline-block w-full bg-green-500 text-white font-bold py-2 px-4 rounded-md hover:bg-green-600"
            >
              Download Processed File
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default BulkProcessor;
