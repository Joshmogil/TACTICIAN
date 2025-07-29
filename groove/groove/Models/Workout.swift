//
//  Workout.swift
//  groove
//
//  Created by Joshua Mogil on 7/28/25.
//

import Foundation



struct Workout: Codable, Hashable, Identifiable {
    var id: UUID
    var day: String
    
    
    struct Exercise: Codable, Hashable, Identifiable {
        var id: UUID
        
        var exercise: String
        var amount: Double
        var actual_amount: Double
        var amount_unit: String
        var intensity: Double
        var actual_intensity: Double
        var intensity_unit: String
        var perceived_exertion: String
        
    }
}
