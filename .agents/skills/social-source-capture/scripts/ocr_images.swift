#!/usr/bin/env swift

import AppKit
import Foundation
import Vision

struct OCRResult: Codable {
    let path: String
    let width: Int
    let height: Int
    let lines: [String]
}

func recognize(path: String) throws -> OCRResult {
    let url = URL(fileURLWithPath: path)
    guard
        let image = NSImage(contentsOf: url),
        let data = image.tiffRepresentation,
        let bitmap = NSBitmapImageRep(data: data),
        let cgImage = bitmap.cgImage
    else {
        throw NSError(
            domain: "ocr_images",
            code: 1,
            userInfo: [NSLocalizedDescriptionKey: "无法读取图片：\(path)"]
        )
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["zh-Hans", "zh-Hant", "en-US"]
    request.usesLanguageCorrection = true
    request.minimumTextHeight = 0.01

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try handler.perform([request])
    let lines = (request.results ?? [])
        .sorted {
            if abs($0.boundingBox.midY - $1.boundingBox.midY) > 0.02 {
                return $0.boundingBox.midY > $1.boundingBox.midY
            }
            return $0.boundingBox.minX < $1.boundingBox.minX
        }
        .compactMap { $0.topCandidates(1).first?.string }

    return OCRResult(path: path, width: cgImage.width, height: cgImage.height, lines: lines)
}

let paths = Array(CommandLine.arguments.dropFirst())
if paths.isEmpty {
    fputs("用法：ocr_images.swift IMAGE...\n", stderr)
    exit(2)
}

var results: [OCRResult] = []
for path in paths {
    do {
        results.append(try recognize(path: path))
    } catch {
        fputs("\(error.localizedDescription)\n", stderr)
        exit(1)
    }
}

let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .withoutEscapingSlashes]
FileHandle.standardOutput.write(try encoder.encode(results))
FileHandle.standardOutput.write(Data("\n".utf8))
