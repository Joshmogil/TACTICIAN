//
//  ExerciseRow.swift
//  groove
//
//  Created by Joshua Mogil on 7/6/25.
//

import SwiftUI

struct ExerciseRow: View {
    let set: ExerciseSet

    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text("\(Int(set.amount)) \(set.amountUnit)")
                if set.intensity > 0 {
                    Text("\(Int(set.intensity)) \(set.intensityUnit)")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }
            Spacer()
            Text(set.perceivedExertion)
                .font(.caption)
                .foregroundColor(color(for: set.perceivedExertion))
                .padding(4)
                .background(Color.gray.opacity(0.2))
                .cornerRadius(4)
        }
    }

    func color(for exertion: String) -> Color {
        switch exertion {
        case "Low": return .green
        case "Medium": return .orange
        case "High": return .red
        default: return .gray
        }
    }
}
