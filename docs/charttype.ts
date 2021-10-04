interface SongFileJson {
    song: {
        player2: string;
        stage?: string;
        gfVersion?: string;
        player1: string;
        speed: number;
        needsVoices: boolean;
        sectionLengths?: any[];
        song: string;
        notes: {
            mustHitSection: boolean;
            typeOfSection?: number;
            lengthInSteps: number;
            sectionNotes: [number, number, number][];
            bpm?: number;
            changeBPM?: boolean;
            altAnim?: boolean;
            altAnimNum?: number;
            endTime?: number;
            startTime?: number;
        }[];
        bpm: number;
        sections?: number;
        validScore?: boolean;
        isHey?: boolean;
        cutsceneType?: string;
        isSpooky?: boolean;
        isMoody?: boolean;
        uiType?: string;
        gf?: string;
        chartVersion?: string;
        eventObjects?: [{
            name: string;
            position: number;
            value: number;
            type: string;
        }],
        noteStyle?: string;
        polus?: string;
    };
}
