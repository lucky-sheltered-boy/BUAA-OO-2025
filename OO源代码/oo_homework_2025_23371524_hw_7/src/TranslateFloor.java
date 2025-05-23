public class TranslateFloor {
    public static Integer getFloorNumber(String floorName) {
        switch (floorName) {
            case "B4":
                return -3;
            case "B3":
                return -2;
            case "B2":
                return -1;
            case "B1":
                return 0;
            case "F1":
                return 1;
            case "F2":
                return 2;
            case "F3":
                return 3;
            case "F4":
                return 4;
            case "F5":
                return 5;
            case "F6":
                return 6;
            case "F7":
                return 7;
            default:
                return null;
        }
    }
    
    public static String getFloorName(Integer floorNumber) {
        switch (floorNumber) {
            case -3:
                return "B4";
            case -2:
                return "B3";
            case -1:
                return "B2";
            case 0:
                return "B1";
            case 1:
                return "F1";
            case 2:
                return "F2";
            case 3:
                return "F3";
            case 4:
                return "F4";
            case 5:
                return "F5";
            case 6:
                return "F6";
            case 7:
                return "F7";
            default:
                return null;
        }
    }
}
