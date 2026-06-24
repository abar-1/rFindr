import React from 'react'
import { useMatch } from '../contexts/MatchContext';

export default function MatchResults() {
    const { matchResults } = useMatch();

    return (
        <div className="bg-gray-50 min-h-screen py-8 px-4">
            {matchResults.length > 0 ? (
                <div className="max-w-3xl mx-auto">
                    <h2 className="text-3xl font-bold mb-6 text-indigo-700 text-center">Your Research Matches</h2>
                    <ul className="space-y-6">
                        {matchResults.map((professor) => (
                            <li 
                                key={professor.professor_id} 
                                className="p-6 border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition-shadow bg-white"
                            >
                                <h3 className="text-2xl font-semibold text-gray-800 mb-2">{professor.name}</h3>
                                {professor.department && (
                                    <p className="text-gray-600 mb-1"><span className="font-medium">Department:</span> {professor.department}</p>
                                )}
                                <p className="text-gray-600 mb-1"><span className="font-medium">Email:</span> {professor.email}</p>
                                <p className="text-gray-600"><span className="font-medium">Similarity Score:</span> {(professor.similarity * 100).toFixed(2)}%</p>
                            </li>
                        ))}
                    </ul>
                </div>
            ) : (
                <p className="mt-12 text-center text-gray-600 text-lg">
                    No matches to display. Please submit your research interests above.
                </p>
            )}
        </div>
    )
}
